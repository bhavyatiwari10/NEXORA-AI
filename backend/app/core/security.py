from datetime import datetime,timedelta,timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
pwd=CryptContext(schemes=['bcrypt'],deprecated='auto')
def hash_password(p): return pwd.hash(p)
def verify_password(p,h): return pwd.verify(p,h)
def make_token(sub,role): return jwt.encode({'sub':sub,'role':role,'exp':datetime.now(timezone.utc)+timedelta(hours=12)},settings.secret_key,algorithm='HS256')
