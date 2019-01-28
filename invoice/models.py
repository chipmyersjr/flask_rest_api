from application import db
from datetime import datetime

from customer.models import Customer
from cart.models import Cart
from cart.models import CartItem
from product.models import Product


class Invoice(db.Document):
    invoice_id = db.StringField(db_field="invoice_id", primary_key=True)
    customer_id = db.ReferenceField(Customer, db_field="customer_id")
    cart_id = db.ReferenceField(Cart, db_field="cart_id")
    state = db.StringField(default="open")
    created_at = db.DateTimeField(default=datetime.now())
    closed_at = db.DateTimeField()

    meta = {
        'indexes': [('customer_id', ), ('cart_id', )]
    }


class InvoiceLineItem(db.Document):
    invoice_line_item_id = db.StringField(db_field="invoice_line_item_id", primary_key=True)
    invoice_id = db.ReferenceField(Invoice, db_field="invoice_id")
    cart_item_id = db.ReferenceField(CartItem, db_field="cart_item_id")
    product_id = db.ReferenceField(Product, db_field="product_id")
    quantity = db.IntField()
    unit_amount = db.DecimalField()
    total_amount = db.DecimalField()
    tax_amount = db.DecimalField()
    type = db.StringField()