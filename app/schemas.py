from pydantic import BaseModel, EmailStr
from typing import List
from typing import Dict

class BillItem(BaseModel):
    product_id: int
    quantity: int


class GenerateBillRequest(BaseModel):
    customer_email: EmailStr
    items: List[BillItem]
    paid_amount: float


class ProductCreate(BaseModel):
    name: str
    stock: int
    price: float
    tax_percent: float

class GenerateBillRequest(BaseModel):
    customer_email: EmailStr
    items: List[BillItem]
    paid_amount: float
    denominations: Dict[int, int]   # {500: 5, 50: 10}
