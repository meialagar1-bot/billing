from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    stock = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    tax_percent = Column(Float, nullable=False)


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, nullable=False)
    total_without_tax = Column(Float)
    total_tax = Column(Float)
    net_total = Column(Float)
    rounded_total = Column(Float)
    paid_amount = Column(Float)
    balance = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("PurchaseItem", back_populates="purchase")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)

    unit_price = Column(Float)
    tax_percent = Column(Float)
    tax_amount = Column(Float)
    total_price = Column(Float)

    purchase = relationship("Purchase", back_populates="items")


class Denomination(Base):
    __tablename__ = "denominations"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, unique=True)
    count = Column(Integer)
