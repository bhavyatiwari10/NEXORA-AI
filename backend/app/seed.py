import sys,os
from datetime import datetime, timedelta
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from app.core.db import Base,engine,SessionLocal
from app.models.models import *
from app.schemas.dto import ConversationIn,MessageIn
from app.pipeline.runner import Pipeline
Base.metadata.create_all(engine); db=SessionLocal()
products=[('Basmati Rice 2kg','BAS-001','1001',5,499,80),('Premium Coffee','COF-001','0901',18,699,35),('Green Tea','TEA-001','0902',12,299,120),('Notebook','NBK-001','4820',12,99,200)]
if not db.query(Product).count():
    for x in products: db.add(Product(name=x[0],sku=x[1],hsn=x[2],gst_rate=x[3],price=x[4],stock=x[5]))
    db.commit()
samples=[
('whatsapp','Ravi','bhai 2 kg basmati rice chahiye, kal tak deliver ho jayega?'),('instagram','Neha','Hi, I need premium coffee. Price kya hai?'),('telegram','Aman','Payment done ₹1398 via UPI, UTR 123456'),('whatsapp','Priya','Please cancel my order and refund.'),('instagram','Sana','Thanks, great service! Can you call me tomorrow?'),('telegram','Karan','Need 20 packs green tea for office, best price?'),('whatsapp','Arjun','Can you send the catalogue?'),('instagram','Meera','I paid 699 yesterday.'),('telegram','Dev','Bhai 5 notebook chahiye urgent.'),('whatsapp','Riya','Delivery Friday confirm kar dena.'),('instagram','Kabir','Very bad service, refund please.'),('telegram','Isha','Can I get 50 coffee packs for my company?'),('whatsapp','Nitin','What is the price of basmati rice?'),('instagram','Tanya','Order 3 green tea packs please.'),('telegram','Rohit','Payment pending, will pay tomorrow.'),('whatsapp','Ananya','Please call me Monday.'),('instagram','Vikas','Need 10 notebooks, bulk discount?'),('telegram','Pooja','Can you change delivery address?'),('whatsapp','Yash','Order cancel karna hai.'),('instagram','Aditi','Thanks, received my package.'),('telegram','Manav','Bhai 2 coffee packs bhej do.'),('whatsapp','Nisha','Can I get GST invoice?'),('instagram','Sahil','UPI payment failed, retry link please.'),('telegram','Diya','Need delivery status.'),('whatsapp','Varun','I am a repeat customer, any discount?'),('instagram','Simran','Please refund ₹499.'),('telegram','Harsh','Kal payment kar dunga.'),('whatsapp','Kavya','Basmati rice ka rate kya hai?'),('instagram','Mohan','Need 100 notebooks urgently.'),('telegram','Aarav','Thank you team, excellent service.')]
for i,(platform,name,text) in enumerate(samples,1):
    eid=f'seed-{i:03d}'
    if not db.query(Conversation).filter(Conversation.external_id==eid).first():
        c=Pipeline(db).ingest(ConversationIn(platform=platform,external_id=eid,customer_name=name,messages=[MessageIn(text=text)])); Pipeline(db).run(c)
        c.created_at=datetime.now()-timedelta(days=(i-1)%7); db.commit()
        for o in db.query(Order).filter(Order.customer_id==c.customer_id).all():
            if o.created_at.date()==datetime.now().date(): o.created_at=c.created_at
        db.commit()
print(f'Seed complete: {db.query(Conversation).count()} conversations, {db.query(Order).count()} orders')

# Add a small realistic finance layer so the demo is useful immediately.
orders=db.query(Order).order_by(Order.id).all()
if orders and db.query(Payment).count()==0:
    for i,o in enumerate(orders[:5]):
        status='success' if i < 3 else ('pending' if i == 3 else 'partial')
        amount=float(o.total) if status in {'success','pending'} else round(float(o.total)*0.5,2)
        db.add(Payment(order_id=o.id,amount=amount,method=['UPI','Card','Bank Transfer','UPI','Card'][i],status=status,reference=f'SIM-{1000+i}'))
        if status=='success': o.status='Paid'
    # Add one realistic high-value pending payment so the Ask NEXORA demo query has a meaningful result.
    largest=max(orders, key=lambda o: float(o.total or 0))
    if not db.query(Payment).filter(Payment.order_id==largest.id, Payment.status=='pending').first():
        db.add(Payment(order_id=largest.id, amount=float(largest.total), method='UPI', status='pending', reference='SIM-PENDING-5001'))
    db.commit()
if orders and db.query(Invoice).count()==0:
    for i,o in enumerate(orders[:5],1):
        db.add(Invoice(order_id=o.id,number=f'NXR/2026-27/{i:04d}',status='issued'))
    db.commit()
print(f'Finance seed: {db.query(Invoice).count()} invoices, {db.query(Payment).count()} payments')
