import re
from app.schemas.dto import ExtractionPayload
def validate_extraction(payload:ExtractionPayload):
    errors=[]; fixes=[]
    if payload.customer and payload.customer.phone and not re.fullmatch(r'(?:\+91[- ]?)?[6-9]\d{9}',payload.customer.phone.value or ''): errors.append('Invalid Indian phone format')
    if payload.customer and payload.customer.pincode and not re.fullmatch(r'[1-9]\d{5}',payload.customer.pincode.value or ''): errors.append('Invalid pincode')
    for p in payload.products:
        if p.quantity<=0: errors.append(f'Quantity must be positive for {p.name}')
    return {'passed':not errors,'auto_fixed':fixes,'failed':errors}
