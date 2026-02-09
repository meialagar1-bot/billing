from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base
from .schemas import GenerateBillRequest, ProductCreate
from .models import Product, Purchase, PurchaseItem, Denomination
from .services import calculate_bill
from typing import List
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Billing System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@app.post("/generate-bill")
def generate_bill(request: GenerateBillRequest, db: Session = Depends(get_db)):
    result = calculate_bill(db, request)
    return result


@app.get("/purchases/{email}")
def get_purchases(email: str, db: Session = Depends(get_db)):
    return db.query(Purchase).filter(Purchase.customer_email == email).all()


@app.get("/purchase/{purchase_id}")
def get_purchase_detail(purchase_id: int, db: Session = Depends(get_db)):
    return db.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase_id).all()
