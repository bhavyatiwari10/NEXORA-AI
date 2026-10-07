from decimal import Decimal,ROUND_HALF_UP

def gst_breakup(subtotal:float,rate:float,seller_state:str,customer_state:str|None):
    tax=(Decimal(str(subtotal))*Decimal(str(rate))/100).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    intra=not customer_state or customer_state.lower()==seller_state.lower()
    return {'subtotal':float(Decimal(str(subtotal)).quantize(Decimal('.01'))),'tax':float(tax),'cgst':float(tax/2) if intra else 0.0,'sgst':float(tax/2) if intra else 0.0,'igst':0.0 if intra else float(tax),'total':float(Decimal(str(subtotal))+tax)}
