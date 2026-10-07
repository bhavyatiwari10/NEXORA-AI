from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from enum import Enum
class Intent(str,Enum): inquiry='inquiry'; order='order'; payment='payment'; follow_up='follow-up'; complaint='complaint'; cancellation='cancellation'; other='other'
class ProductExtract(BaseModel):
    name:str; sku_match:str|None=None; quantity:float=Field(gt=0); unit:str='unit'; price:float|None=None; confidence:float=Field(ge=0,le=1); source_span:str=''
class FieldEvidence(BaseModel): value:str|None=None; confidence:float=Field(ge=0,le=1); source_span:str=''
class CustomerExtract(BaseModel):
    name:FieldEvidence|None=None; phone:FieldEvidence|None=None; email:FieldEvidence|None=None; address:FieldEvidence|None=None; city:FieldEvidence|None=None; pincode:FieldEvidence|None=None; gstin:FieldEvidence|None=None
class PaymentExtract(BaseModel):
    status:str='unknown'; amount:float|None=None; method:str|None=None; reference:str|None=None; confidence:float=.5; source_span:str=''
class FollowUpExtract(BaseModel):
    date_time:datetime|None=None; reason:str|None=None; confidence:float=.5; source_span:str=''
class ExtractionPayload(BaseModel):
    customer:CustomerExtract|None=None; intent:Intent=Intent.other; products:list[ProductExtract]=[]; delivery_date:date|None=None; delivery_mode:str|None=None; payment:PaymentExtract|None=None; follow_up:FollowUpExtract|None=None; sentiment:str='neutral'; language:str='English'; summary:str=''; confidence:float=.5
class MessageIn(BaseModel): sender:str='customer'; text:str; timestamp:datetime|None=None
class ConversationIn(BaseModel): platform:str='whatsapp'; external_id:str; messages:list[MessageIn]; customer_name:str|None=None
class QuerySpec(BaseModel): metric:str; dimensions:list[str]=[]; filters:dict[str,str|float|int|None]={}; date_range:str='all'; chart_type:str='bar'; limit:int=10
class AskRequest(BaseModel): question:str
