from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import Base,engine
from app.models import *
from app.api.routes import router
Base.metadata.create_all(engine)
app=FastAPI(title='Nexora AI API',version='1.0.0',description='AI/NLP conversational CRM and visual analytics platform')
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(',')],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(router)
@app.get('/')
def root(): return {'name':'Nexora','research':'A Unified User-Centric Evaluation Framework for Large Language Models in Conversational Visual Analytics'}
