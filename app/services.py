from sqlalchemy.orm import Session
from .models import Product, Purchase, PurchaseItem, Denomination
from fastapi import HTTPException, BackgroundTasks
import math

def calculate_denominations(balance, available_denoms):
    result = {}

    for value in sorted(available_denoms.keys(), reverse=True):
        available_count = available_denoms[value]

        needed = balance // value
        used = min(needed, available_count)

        if used > 0:
            result[value] = used
            balance -= used * value

    if balance != 0:
        raise HTTPException(
            status_code=400,
            detail="Insufficient denomination balance in shop"
        )

    return result


def calculate_bill(db: Session, request):

    total_without_tax = 0
    total_tax = 0
    purchase_items = []

    for item in request.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        unit_price = product.price
        tax_amount = unit_price * (product.tax_percent / 100) * item.quantity
        total_price = unit_price * item.quantity

        total_without_tax += total_price
        total_tax += tax_amount

        product.stock -= item.quantity

        purchase_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "tax_percent": product.tax_percent,
            "tax_amount": tax_amount,
            "total_price": total_price
        })

    net_total = total_without_tax + total_tax
    rounded_total = int(net_total)

    balance = request.paid_amount - rounded_total

    if balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient payment")

    # 🔥 DENOMINATION CALCULATION
    balance_distribution = calculate_denominations(
        int(balance),
        request.denominations
    )

    purchase = Purchase(
        customer_email=request.customer_email,
        total_without_tax=total_without_tax,
        total_tax=total_tax,
        net_total=net_total,
        rounded_total=rounded_total,
        paid_amount=request.paid_amount,
        balance=balance
    )

    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    for item in purchase_items:
        db_item = PurchaseItem(
            purchase_id=purchase.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            tax_percent=item["tax_percent"],
            tax_amount=item["tax_amount"],
            total_price=item["total_price"]
        )
        db.add(db_item)

    db.commit()

    return {
        "purchase_id": purchase.id,
        "balance": balance,
        "denominations": balance_distribution
    }
