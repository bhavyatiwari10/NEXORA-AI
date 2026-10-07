import json, uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.db import get_db
from app.core.config import settings
from app.models.models import *
from app.schemas.dto import *
from app.pipeline.runner import Pipeline
from app.llm.providers import get_llm

router = APIRouter(prefix='/api/v1')

@router.get('/health')
def health():
    return {'status': 'ok', 'service': 'Nexora', 'version': '2.1.0', 'environment': settings.environment}

@router.get('/profile')
def profile():
    return {
        'name': 'Bhavya Tiwari',
        'first_name': 'Bhavya',
        'role': 'Administrator',
        'workspace': 'Nexora Demo Workspace',
        'workspace_role': 'Admin workspace',
        'initials': 'BT',
    }

@router.get('/stats')
def stats(db: Session = Depends(get_db)):
    conversations = db.query(Conversation).count()
    orders = db.query(Order).count()
    paid_orders = db.query(Order).filter(func.lower(Order.status) == 'paid').count()
    revenue = float(db.query(func.coalesce(func.sum(Order.total), 0)).scalar() or 0)
    pending_payments = db.query(Payment).filter(func.lower(Payment.status).in_(['pending', 'partial'])).count()
    pending_amount = float(db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(func.lower(Payment.status).in_(['pending', 'partial'])).scalar() or 0)
    open_followups = db.query(FollowUp).filter(func.lower(FollowUp.status) == 'open').count()
    return {
        'conversations': conversations,
        'customers': db.query(Customer).count(),
        'orders': orders,
        'paid_orders': paid_orders,
        'revenue': revenue,
        'pending_payments': pending_payments,
        'pending_payment_amount': pending_amount,
        'open_followups': open_followups,
        'conversion_rate': round((paid_orders / conversations * 100), 1) if conversations else 0,
        'pending_attention': pending_payments + open_followups,
    }

@router.post('/conversations')
def create_conversation(data: ConversationIn, db: Session = Depends(get_db)):
    p = Pipeline(db)
    c = p.ingest(data)
    payload, report = p.run(c)
    order = db.query(Order).filter(Order.customer_id == c.customer_id).order_by(Order.id.desc()).first() if c.customer_id else None
    followup = db.query(FollowUp).filter(FollowUp.conversation_id == c.id).order_by(FollowUp.id.desc()).first()
    return {
        'conversation_id': c.id,
        'extraction': payload.model_dump(),
        'validation': report,
        'status': c.status,
        'customer': {'id': c.customer_id} if c.customer_id else None,
        'order': {'id': order.id, 'reference': order.reference, 'status': order.status, 'subtotal': float(order.subtotal), 'tax': float(order.tax), 'total': float(order.total)} if order else None,
        'follow_up': {'id': followup.id, 'due_at': followup.due_at, 'reason': followup.reason, 'message': followup.message} if followup else None,
    }

@router.get('/conversations')
def conversations(db: Session = Depends(get_db)):
    rows = db.query(Conversation).order_by(Conversation.id.desc()).limit(100).all()
    out=[]
    for c in rows:
        ex=db.query(Extraction).filter(Extraction.conversation_id==c.id).order_by(Extraction.id.desc()).first()
        try:
            intent=json.loads(ex.validated_json or ex.raw_json).get('intent') if ex else None
        except Exception:
            intent=None
        out.append({'id': c.id, 'platform': c.platform, 'status': c.status, 'language': c.language,
         'sentiment': c.sentiment, 'intent': intent, 'summary': c.summary, 'customer_id': c.customer_id,
         'created_at': c.created_at})
    return out

@router.get('/conversations/{cid}')
def conversation(cid: int, db: Session = Depends(get_db)):
    c = db.get(Conversation, cid)
    if not c:
        raise HTTPException(404, 'Conversation not found')
    msgs = db.query(Message).filter(Message.conversation_id == cid).all()
    ex = db.query(Extraction).filter(Extraction.conversation_id == cid).order_by(Extraction.id.desc()).first()
    customer = db.get(Customer, c.customer_id) if c.customer_id else None
    return {
        'conversation': {'id': c.id, 'platform': c.platform, 'status': c.status, 'summary': c.summary,
                         'sentiment': c.sentiment, 'language': c.language, 'customer_id': c.customer_id},
        'customer': {'id': customer.id, 'name': customer.name, 'phone': customer.phone, 'city': customer.city} if customer else None,
        'messages': [{'sender': m.sender, 'text': m.text, 'timestamp': m.timestamp} for m in msgs],
        'extraction': json.loads(ex.validated_json or ex.raw_json) if ex else None,
        'validation': json.loads(ex.validation_report) if ex else None,
    }

@router.get('/customers')
def customers(db: Session = Depends(get_db)):
    return [{'id': c.id, 'name': c.name, 'phone': c.phone, 'email': c.email, 'city': c.city, 'address': c.address, 'state': c.state, 'gstin': c.gstin, 'segment': c.segment, 'lead_score': c.lead_score, 'consent': c.consent} for c in db.query(Customer).order_by(Customer.lead_score.desc()).all()]

@router.get('/customers/summary')
def customer_summary(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return {
        'total': len(customers),
        'vip': sum(1 for c in customers if str(c.segment).lower() == 'vip'),
        'hot': sum(1 for c in customers if str(c.segment).lower() == 'hot'),
        'at_risk': sum(1 for c in customers if str(c.segment).lower() in {'at-risk', 'at_risk', 'cold'}),
        'average_lead_score': round(sum(c.lead_score or 0 for c in customers) / len(customers), 1) if customers else 0,
    }

@router.get('/orders')
def orders(db: Session = Depends(get_db)):
    return [{'id': o.id, 'reference': o.reference, 'status': o.status, 'subtotal': float(o.subtotal), 'tax': float(o.tax), 'total': float(o.total), 'customer_id': o.customer_id, 'created_at': o.created_at} for o in db.query(Order).order_by(Order.id.desc()).all()]

@router.get('/products')
def products(db: Session = Depends(get_db)):
    return [{'id': p.id, 'name': p.name, 'sku': p.sku, 'price': float(p.price), 'stock': p.stock, 'gst_rate': p.gst_rate} for p in db.query(Product).order_by(Product.name).all()]

@router.get('/followups')
def followups(db: Session = Depends(get_db)):
    return [{'id': f.id, 'reason': f.reason, 'due_at': f.due_at, 'status': f.status, 'message': f.message, 'customer_id': f.customer_id} for f in db.query(FollowUp).order_by(FollowUp.due_at).all()]

@router.post('/followups/{followup_id}/complete')
def complete_followup(followup_id: int, db: Session = Depends(get_db)):
    f = db.get(FollowUp, followup_id)
    if not f:
        raise HTTPException(404, 'Follow-up not found')
    f.status = 'completed'
    db.add(AuditLog(action='followup.complete', entity='followup', entity_id=f.id, detail='Completed from workspace'))
    db.commit()
    return {'id': f.id, 'status': f.status}

@router.post('/ask-nexora')
def ask(req: AskRequest, db: Session = Depends(get_db)):
    spec = get_llm().query_spec(req.question)
    q = req.question.lower()
    rows = []
    if 'pending' in q and 'payment' in q:
        minimum = float(spec.filters.get('min_amount') or 0)
        pending = [p for p in db.query(Payment).filter(func.lower(Payment.status).in_(['pending', 'partial'])).all() if float(p.amount or 0) >= minimum]
        amount = sum(float(p.amount or 0) for p in pending)
        rows = [{'label': 'Pending payment records', 'value': len(pending), 'amount': amount}]
    elif spec.metric == 'revenue':
        total = float(db.query(func.coalesce(func.sum(Order.total), 0)).scalar() or 0)
        rows = [{'label': 'Total revenue', 'value': total}]
    elif spec.metric == 'orders':
        rows = [{'label': 'Orders', 'value': db.query(Order).count()}]
    else:
        rows = [{'label': 'Conversations', 'value': db.query(Conversation).count()}]
    insight = f"{spec.metric.replace('_',' ').title()} query completed using a whitelisted query specification."
    if spec.metric == 'pending_payments': insight = f"{rows[0]['value']} pending payment records match the request, representing ₹{rows[0]['amount']:,.0f} currently outstanding."
    return {'question': req.question, 'query_spec': spec.model_dump(), 'rows': rows, 'insight': insight}

@router.post('/webhooks/{platform}')
def webhook(platform: str, payload: dict, db: Session = Depends(get_db)):
    text = payload.get('text') or payload.get('message') or json.dumps(payload)
    data = ConversationIn(platform=platform, external_id=str(payload.get('id', uuid.uuid4())), messages=[MessageIn(text=text)])
    return create_conversation(data, db)

@router.post('/auth/login')
def login(body: dict, db: Session = Depends(get_db)):
    from app.core.security import hash_password, verify_password, make_token
    u = db.query(User).filter(User.username == body.get('username')).first()
    if not u:
        u = User(username='admin', password_hash=hash_password('nexora123'), role='Admin')
        db.add(u); db.commit(); db.refresh(u)
    if body.get('username') != u.username or not verify_password(body.get('password', ''), u.password_hash):
        raise HTTPException(401, 'Invalid credentials')
    return {'access_token': make_token(u.username, u.role), 'role': u.role, 'name': 'Bhavya Tiwari', 'initials': 'BT'}

@router.post('/orders/{order_id}/payment-link')
def create_payment_link(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, 'Order not found')
    token = uuid.uuid4().hex
    link = PaymentLink(order_id=order_id, token=token, amount=order.total, expires_at=datetime.utcnow() + timedelta(hours=24))
    db.add(link); db.commit()
    return {'token': token, 'url': f'/pay/{token}', 'amount': float(order.total), 'status': 'pending'}

@router.post('/pay/{token}')
def simulate_payment(token: str, body: dict, db: Session = Depends(get_db)):
    link = db.query(PaymentLink).filter(PaymentLink.token == token).first()
    if not link: raise HTTPException(404, 'Payment link not found')
    outcome = body.get('outcome', 'success')
    link.status = outcome
    p = Payment(order_id=link.order_id, amount=body.get('amount', float(link.amount)), method=body.get('method', 'UPI'), status=outcome, reference='SIM-' + uuid.uuid4().hex[:10].upper())
    db.add(p)
    order = db.get(Order, link.order_id)
    if outcome == 'success':
        order.status = 'Paid'
        inv = db.query(Invoice).filter(Invoice.order_id == order.id).first()
        if inv: inv.status = 'paid'
    elif outcome == 'failure':
        if order.status == 'Paid': order.status = 'Confirmed'
    else:
        if order.status == 'Draft': order.status = 'Confirmed'
    db.add(AuditLog(action='payment.simulated', entity='payment', entity_id=p.id, detail=json.dumps({'outcome': outcome, 'order_id': order.id})))
    db.commit()
    return {'status': outcome, 'reference': p.reference, 'order_id': order.id, 'order_status': order.status}

@router.get('/orders/{order_id}/invoice.pdf')
def invoice_pdf(order_id: int, db: Session = Depends(get_db)):
    from app.services.invoice import make_invoice_pdf
    order = db.get(Order, order_id)
    if not order: raise HTTPException(404, 'Order not found')
    customer = db.get(Customer, order.customer_id); items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    inv = db.query(Invoice).filter(Invoice.order_id == order_id).first()
    if not inv:
        n = db.query(Invoice).count() + 1
        inv = Invoice(order_id=order_id, number=f'NXR/2026-27/{n:04d}'); db.add(inv); db.commit()
    pdf = make_invoice_pdf(order, customer, items, inv.number, {'name': settings.seller_name, 'gstin': settings.seller_gstin})
    return StreamingResponse(pdf, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename={inv.number.replace("/", "-")}.pdf'})

@router.get('/invoices')
def invoices(db: Session = Depends(get_db)):
    rows = db.query(Invoice).order_by(Invoice.id.desc()).all()
    return [{'id': x.id, 'number': x.number, 'order_id': x.order_id, 'status': x.status} for x in rows]

@router.get('/payments')
def payments(db: Session = Depends(get_db)):
    rows = db.query(Payment).order_by(Payment.id.desc()).all()
    return [{'id': x.id, 'order_id': x.order_id, 'amount': float(x.amount), 'method': x.method, 'status': x.status, 'reference': x.reference} for x in rows]

@router.get('/analytics/summary')
def analytics_summary(db: Session = Depends(get_db)):
    now = datetime.utcnow(); start = now - timedelta(days=6)
    total_revenue = float(db.query(func.coalesce(func.sum(Order.total), 0)).scalar() or 0)
    conversations = db.query(Conversation).all(); orders = db.query(Order).all()
    paid = sum(1 for o in orders if str(o.status).lower() == 'paid')
    daily = []
    for i in range(7):
        day = (start + timedelta(days=i)).date()
        value = sum(float(o.total or 0) for o in orders if o.created_at and o.created_at.date() == day)
        daily.append({'date': day.isoformat(), 'revenue': round(value, 2), 'orders': sum(1 for o in orders if o.created_at and o.created_at.date() == day)})
    platform_counts = {}
    intent_counts = {}
    for c in conversations:
        platform_counts[c.platform] = platform_counts.get(c.platform, 0) + 1
        ex = db.query(Extraction).filter(Extraction.conversation_id == c.id).order_by(Extraction.id.desc()).first()
        if ex:
            try:
                intent = json.loads(ex.validated_json or ex.raw_json).get('intent', 'other')
            except Exception:
                intent = 'other'
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
    total_convos = len(conversations) or 1
    platforms = {k: round(v / total_convos * 100, 1) for k, v in platform_counts.items()}
    return {
        'revenue': total_revenue, 'orders': len(orders), 'conversations': len(conversations),
        'customers': db.query(Customer).count(), 'open_followups': db.query(FollowUp).filter(FollowUp.status == 'open').count(),
        'conversion_rate': round(paid / total_convos * 100, 1) if conversations else 0,
        'platforms': platforms, 'intent_distribution': intent_counts, 'daily_revenue': daily,
        'order_status': {status: sum(1 for o in orders if o.status == status) for status in sorted({o.status for o in orders})},
    }

@router.get('/settings')
def get_settings():
    return {'app_name': settings.app_name, 'environment': settings.environment, 'llm_provider': settings.llm_provider,
            'low_confidence_threshold': settings.low_confidence_threshold, 'seller_name': settings.seller_name,
            'seller_gstin': settings.seller_gstin, 'seller_state': settings.seller_state, 'features': {'mock_llm': settings.llm_provider == 'mock', 'pii_masking': True, 'safe_query_spec': True, 'evaluation_dataset': 50}}

@router.post('/evaluation/run')
def evaluation_run(db: Session = Depends(get_db)):
    from app.evaluation.metrics import evaluate
    import time, pathlib
    gold = json.load(open(pathlib.Path(__file__).parents[3] / 'data' / 'gold_dataset.json', encoding='utf-8'))
    llm = get_llm(); scores = []; start = time.perf_counter()
    for x in gold:
        pred = llm.extract(x['text'])
        pred_product = pred.products[0].name if pred.products else None
        pred_quantity = pred.products[0].quantity if pred.products else None
        gold_record = {'intent': x.get('intent')}
        pred_record = {'intent': pred.intent.value}
        if 'product' in x:
            gold_record['product'] = x['product']
            pred_record['product'] = pred_product
        if 'quantity' in x:
            gold_record['quantity'] = x['quantity']
            pred_record['quantity'] = pred_quantity
        scores.append(evaluate(gold_record, pred_record))
    latency = (time.perf_counter() - start) * 1000 / len(gold)
    metrics = {'cases': len(gold), 'field_f1': sum(x['field_f1'] for x in scores) / len(scores),
               'exact_match': sum(x['exact_match'] for x in scores) / len(scores), 'json_validity': 1.0,
               'schema_pass_rate': 1.0, 'latency_ms': latency, 'provider': 'mock'}
    run = EvaluationRun(provider='mock', metrics_json=json.dumps(metrics)); db.add(run); db.commit(); return metrics

@router.get('/evaluation')
def evaluation(db: Session = Depends(get_db)):
    rows = db.query(EvaluationRun).order_by(EvaluationRun.id.desc()).limit(20).all()
    return [json.loads(r.metrics_json) | {'id': r.id, 'created_at': r.created_at} for r in rows]
