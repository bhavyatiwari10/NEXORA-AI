import json
from sqlalchemy.orm import Session
from app.llm.providers import get_llm
from app.models.models import Conversation,Message,Extraction,Customer,Product,Order,OrderItem,FollowUp,AuditLog
from app.services.validation import validate_extraction
from app.services.gst import gst_breakup
class Pipeline:
    def __init__(self,db:Session): self.db=db; self.llm=get_llm()
    def ingest(self, data):
        c=Conversation(platform=data.platform,external_id=data.external_id,status='received',title=data.customer_name or 'New conversation'); self.db.add(c); self.db.flush()
        if data.customer_name:
            customer=self.db.query(Customer).filter(Customer.name.ilike(data.customer_name)).first()
            if not customer:
                customer=Customer(name=data.customer_name,lead_score=55,segment='warm'); self.db.add(customer); self.db.flush()
            c.customer_id=customer.id
        for m in data.messages: self.db.add(Message(conversation_id=c.id,sender=m.sender,text=m.text,timestamp=m.timestamp))
        self.db.flush()
        return c
    def run(self,c:Conversation):
        texts='\n'.join(m.text for m in c.__dict__.get('messages',[]) ) if False else '\n'.join(x.text for x in self.db.query(Message).filter(Message.conversation_id==c.id).all())
        payload=self.llm.extract(texts); report=validate_extraction(payload)
        ex=Extraction(conversation_id=c.id,raw_json=payload.model_dump_json(),validated_json=payload.model_dump_json() if report['passed'] else None,status='passed' if report['passed'] else 'review',validation_report=json.dumps(report)); self.db.add(ex)
        if payload.customer or c.customer_id:
            ce=payload.customer
            phone=ce.phone.value if ce and ce.phone else None
            customer=self.db.get(Customer,c.customer_id) if c.customer_id else (self.db.query(Customer).filter(Customer.phone==phone).first() if phone else None)
            if not customer:
                customer=Customer(name=(ce.name.value if ce and ce.name else 'Unknown'),phone=phone,email=ce.email.value if ce and ce.email else None,pincode=ce.pincode.value if ce and ce.pincode else None); self.db.add(customer); self.db.flush()
            if payload.intent.value=='order':
                customer.lead_score=min(100, max(customer.lead_score or 0, 85))
                customer.segment='hot' if customer.lead_score >= 80 else 'warm'
            elif payload.intent.value=='complaint':
                customer.segment='at-risk'
            c.customer_id=customer.id; c.language=payload.language; c.sentiment=payload.sentiment; c.summary=payload.summary
        if payload.intent.value=='order' and payload.products and report['passed'] and c.customer_id:
            ref=f'NXR-{c.id:05d}'; order=Order(reference=ref,customer_id=c.customer_id,status='Draft'); self.db.add(order); self.db.flush(); subtotal=0.0; weighted_tax_value=0.0
            for p in payload.products:
                prod=self.db.query(Product).filter(Product.sku==p.sku_match).first() if p.sku_match else None
                if prod:
                    price=float(p.price or prod.price)
                    line_value=price*float(p.quantity)
                    subtotal += line_value
                    weighted_tax_value += line_value*float(prod.gst_rate)
                    self.db.add(OrderItem(order_id=order.id,product_id=prod.id,quantity=p.quantity,unit_price=price,tax_rate=prod.gst_rate))
                    prod.stock=max(0,prod.stock-int(p.quantity))
            if subtotal:
                weighted_rate = weighted_tax_value / subtotal
                b=gst_breakup(subtotal, weighted_rate, 'Uttar Pradesh', None)
                order.subtotal=b['subtotal']; order.tax=b['tax']; order.total=b['total']
        if payload.follow_up and c.customer_id: self.db.add(FollowUp(customer_id=c.customer_id,conversation_id=c.id,due_at=payload.follow_up.date_time,reason=payload.follow_up.reason or 'Follow-up',message=self.llm.generate_reply(texts,payload.language)))
        c.status='validated' if report['passed'] else 'needs_review'; self.db.add(AuditLog(action='pipeline.run',entity='conversation',entity_id=c.id,detail=json.dumps(report))); self.db.commit(); self.db.refresh(c); return payload,report
