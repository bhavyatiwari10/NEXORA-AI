from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, DateTime, Date, Float, Integer, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
class Customer(Base):
    __tablename__='customers'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(120))
    phone: Mapped[str|None]=mapped_column(String(20),index=True)
    email: Mapped[str|None]=mapped_column(String(160))
    address: Mapped[str|None]=mapped_column(Text)
    city: Mapped[str|None]=mapped_column(String(80))
    pincode: Mapped[str|None]=mapped_column(String(10))
    gstin: Mapped[str|None]=mapped_column(String(20))
    state: Mapped[str|None]=mapped_column(String(80))
    consent: Mapped[bool]=mapped_column(Boolean,default=True)
    lead_score: Mapped[float]=mapped_column(Float,default=0)
    segment: Mapped[str]=mapped_column(String(20),default='warm')
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Product(Base):
    __tablename__='products'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(160),index=True)
    sku: Mapped[str]=mapped_column(String(50),unique=True)
    hsn: Mapped[str]=mapped_column(String(20))
    gst_rate: Mapped[float]=mapped_column(Float,default=18)
    price: Mapped[float]=mapped_column(Numeric(12,2))
    stock: Mapped[int]=mapped_column(Integer,default=0)
class Conversation(Base):
    __tablename__='conversations'
    id: Mapped[int]=mapped_column(primary_key=True)
    platform: Mapped[str]=mapped_column(String(30))
    external_id: Mapped[str]=mapped_column(String(100),index=True)
    customer_id: Mapped[int|None]=mapped_column(ForeignKey('customers.id'))
    title: Mapped[str|None]=mapped_column(String(200))
    status: Mapped[str]=mapped_column(String(30),default='received')
    language: Mapped[str|None]=mapped_column(String(30))
    sentiment: Mapped[str|None]=mapped_column(String(30))
    summary: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    customer=relationship('Customer')
class Message(Base):
    __tablename__='messages'
    id: Mapped[int]=mapped_column(primary_key=True)
    conversation_id: Mapped[int]=mapped_column(ForeignKey('conversations.id'))
    sender: Mapped[str]=mapped_column(String(20))
    text: Mapped[str]=mapped_column(Text)
    timestamp: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    conversation=relationship('Conversation')
class Extraction(Base):
    __tablename__='extractions'
    id: Mapped[int]=mapped_column(primary_key=True)
    conversation_id: Mapped[int]=mapped_column(ForeignKey('conversations.id'))
    raw_json: Mapped[str]=mapped_column(Text)
    validated_json: Mapped[str|None]=mapped_column(Text)
    status: Mapped[str]=mapped_column(String(30),default='pending')
    validation_report: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Order(Base):
    __tablename__='orders'
    id: Mapped[int]=mapped_column(primary_key=True)
    reference: Mapped[str]=mapped_column(String(40),unique=True)
    customer_id: Mapped[int]=mapped_column(ForeignKey('customers.id'))
    status: Mapped[str]=mapped_column(String(30),default='Draft')
    subtotal: Mapped[float]=mapped_column(Numeric(12,2),default=0)
    tax: Mapped[float]=mapped_column(Numeric(12,2),default=0)
    total: Mapped[float]=mapped_column(Numeric(12,2),default=0)
    delivery_date: Mapped[Date|None]=mapped_column(Date)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    customer=relationship('Customer')
class OrderItem(Base):
    __tablename__='order_items'
    id: Mapped[int]=mapped_column(primary_key=True)
    order_id: Mapped[int]=mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int]=mapped_column(ForeignKey('products.id'))
    quantity: Mapped[float]=mapped_column(Float)
    unit_price: Mapped[float]=mapped_column(Numeric(12,2))
    tax_rate: Mapped[float]=mapped_column(Float)
    order=relationship('Order')
    product=relationship('Product')
class Invoice(Base):
    __tablename__='invoices'
    id: Mapped[int]=mapped_column(primary_key=True)
    order_id: Mapped[int]=mapped_column(ForeignKey('orders.id'))
    number: Mapped[str]=mapped_column(String(50),unique=True)
    status: Mapped[str]=mapped_column(String(20),default='issued')
    pdf_path: Mapped[str|None]=mapped_column(String(300))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Payment(Base):
    __tablename__='payments'
    id: Mapped[int]=mapped_column(primary_key=True)
    order_id: Mapped[int]=mapped_column(ForeignKey('orders.id'))
    amount: Mapped[float]=mapped_column(Numeric(12,2))
    method: Mapped[str]=mapped_column(String(30))
    status: Mapped[str]=mapped_column(String(30))
    reference: Mapped[str|None]=mapped_column(String(80))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class PaymentLink(Base):
    __tablename__='payment_links'
    id: Mapped[int]=mapped_column(primary_key=True)
    order_id: Mapped[int]=mapped_column(ForeignKey('orders.id'))
    token: Mapped[str]=mapped_column(String(80),unique=True)
    amount: Mapped[float]=mapped_column(Numeric(12,2))
    status: Mapped[str]=mapped_column(String(20),default='pending')
    expires_at: Mapped[datetime|None]=mapped_column(DateTime)
class FollowUp(Base):
    __tablename__='followups'
    id: Mapped[int]=mapped_column(primary_key=True)
    customer_id: Mapped[int]=mapped_column(ForeignKey('customers.id'))
    conversation_id: Mapped[int|None]=mapped_column(ForeignKey('conversations.id'))
    due_at: Mapped[datetime]
    reason: Mapped[str]=mapped_column(String(200))
    message: Mapped[str|None]=mapped_column(Text)
    status: Mapped[str]=mapped_column(String(20),default='open')
    assigned_to: Mapped[str|None]=mapped_column(String(100))
class AuditLog(Base):
    __tablename__='audit_logs'
    id: Mapped[int]=mapped_column(primary_key=True)
    action: Mapped[str]=mapped_column(String(100))
    entity: Mapped[str]=mapped_column(String(50))
    entity_id: Mapped[int|None]=mapped_column(Integer)
    detail: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class EvaluationRun(Base):
    __tablename__='evaluation_runs'
    id: Mapped[int]=mapped_column(primary_key=True)
    provider: Mapped[str]=mapped_column(String(40))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    metrics_json: Mapped[str]=mapped_column(Text)
class EvaluationResult(Base):
    __tablename__='evaluation_results'
    id: Mapped[int]=mapped_column(primary_key=True)
    run_id: Mapped[int]=mapped_column(ForeignKey('evaluation_runs.id'))
    case_id: Mapped[str]=mapped_column(String(80))
    exact_match: Mapped[bool]
    field_precision: Mapped[float]
    field_recall: Mapped[float]
    field_f1: Mapped[float]
    latency_ms: Mapped[float]
    corrections: Mapped[int]=mapped_column(Integer,default=0)
class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    username: Mapped[str]=mapped_column(String(80),unique=True)
    password_hash: Mapped[str]=mapped_column(String(200))
    role: Mapped[str]=mapped_column(String(30),default='Viewer')
