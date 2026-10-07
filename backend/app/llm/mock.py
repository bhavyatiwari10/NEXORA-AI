import re
from datetime import date, datetime, timedelta
from app.llm.base import LLMProvider
from app.schemas.dto import *


class MockLLM(LLMProvider):
    """Deterministic, offline-first extractor used for demos, tests and fallback operation."""

    def extract(self, text: str) -> ExtractionPayload:
        low = text.lower()
        phone = re.search(r'(?:\+91[- ]?)?[6-9]\d{9}', text)
        email = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        pin = re.search(r'\b[1-9]\d{5}\b', text)

        name = None
        m = re.search(r'(?:i am|my name is|name is)\s+([A-Za-z ]{2,40})', text, re.I)
        if m:
            name = m.group(1).strip()

        products = []
        catalogue = [
            ('basmati rice', ('basmati rice', 'basmati'), 'BAS-001'),
            ('premium coffee', ('premium coffee', 'coffee'), 'COF-001'),
            ('green tea', ('green tea', 'tea'), 'TEA-001'),
            ('notebook', ('notebook', 'notebooks'), 'NBK-001'),
        ]
        for product_name, aliases, sku in catalogue:
            matched = next((alias for alias in aliases if alias in low), None)
            if not matched:
                continue
            qm = re.search(
                r'(\d+(?:\.\d+)?)\s*(?:kg|kgs|pack|packs|pcs|pieces)?\s*' + re.escape(matched),
                low,
            )
            qty = float(qm.group(1)) if qm else 1
            unit = 'kg' if qm and 'kg' in qm.group(0) else 'unit'
            products.append(ProductExtract(
                name=product_name,
                sku_match=sku,
                quantity=qty,
                unit=unit,
                price=None,
                confidence=.94,
                source_span=qm.group(0) if qm else matched,
            ))

        intent = Intent.order if products or 'order' in low or 'chahiye' in low else Intent.inquiry
        if any(x in low for x in ['paid', 'payment done', 'utr']):
            intent = Intent.payment
        if any(x in low for x in ['refund', 'complaint', 'angry', 'bad service']):
            intent = Intent.complaint
        if any(x in low for x in ['cancel', 'cancellation']):
            intent = Intent.cancellation

        lang = 'Hinglish' if any(x in low for x in ['bhai', 'chahiye', 'kal', 'ho jayega', 'kitne', 'hai']) else 'English'
        sentiment = 'negative' if intent == Intent.complaint else ('positive' if any(x in low for x in ['thanks', 'thank you', 'great', 'excellent']) else 'neutral')

        payment = None
        if 'paid' in low or 'payment' in low:
            amount_match = re.search(r'(?:₹|rs\.?\s*)([\d,]+(?:\.\d+)?)', low)
            payment = PaymentExtract(
                status='paid' if 'paid' in low or 'done' in low else 'pending',
                amount=float(amount_match.group(1).replace(',', '')) if amount_match else None,
                method='UPI' if 'upi' in low else None,
                confidence=.9,
                source_span='payment',
            )

        follow = None
        if any(x in low for x in ['tomorrow', 'kal', 'friday', 'monday']):
            follow = FollowUpExtract(
                date_time=datetime.now() + timedelta(days=1),
                reason='Customer-requested follow-up',
                confidence=.78,
                source_span='tomorrow/kal',
            )

        customer = CustomerExtract(
            name=FieldEvidence(value=name, confidence=.9, source_span=m.group(0)) if name else None,
            phone=FieldEvidence(value=phone.group(0), confidence=.99, source_span=phone.group(0)) if phone else None,
            email=FieldEvidence(value=email.group(0), confidence=.99, source_span=email.group(0)) if email else None,
            pincode=FieldEvidence(value=pin.group(0), confidence=.95, source_span=pin.group(0)) if pin else None,
        )
        return ExtractionPayload(
            customer=customer,
            intent=intent,
            products=products,
            delivery_date=(date.today() + timedelta(days=1)) if any(x in low for x in ['tomorrow', 'kal']) else None,
            payment=payment,
            follow_up=follow,
            sentiment=sentiment,
            language=lang,
            summary=text[:180],
            confidence=.94 if products else .9,
        )

    def generate_reply(self, text, language='English') -> str:
        return (
            'Thanks! I have captured your request. Our team will confirm the details shortly.'
            if language == 'English'
            else 'Thanks bhai! Aapki request note kar li hai. Team jaldi confirm karegi.'
        )

    def query_spec(self, question: str):
        q = question.lower()
        if 'pending' in q and 'payment' in q:
            m = re.search(r'(?:₹|rs\.?\s*)?([\d,]+)', q)
            minimum = float(m.group(1).replace(',', '')) if m else 0
            return QuerySpec(metric='pending_payments', dimensions=['customer'], filters={'min_amount': minimum}, chart_type='bar', limit=10)
        metric = 'revenue' if 'revenue' in q or 'sales' in q else ('orders' if 'order' in q else 'conversations')
        dims = ['platform'] if 'platform' in q else (['status'] if 'status' in q else [])
        chart = 'line' if 'over time' in q or 'trend' in q else ('pie' if dims == ['platform'] else 'bar')
        return QuerySpec(metric=metric, dimensions=dims, chart_type=chart, limit=10)
