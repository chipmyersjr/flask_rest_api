from application import db
from datetime import datetime
import uuid

from invoice.models import Invoice, InvoiceLineItem
from product.models import Product


class Order(db.Document):
    order_id = db.StringField(db_field="order_id", primary_key=True)
    invoice = db.ReferenceField(Invoice, db_field="invoice_id")
    status = db.StringField(default='pending')
    created_at = db.DateTimeField(default=datetime.now())
    shipped_at = db.DateTimeField()
    delivered_at = db.DateTimeField()
    canceled_at = db.DateTimeField()


class OrderLineItem(db.Document):
    order_line_item_id = db.StringField(order_line_item_id="invoice_id", primary_key=True)
    order = db.ReferenceField(Order, db_field="order_id")
    invoice_line_item = db.ReferenceField(InvoiceLineItem, db_field="invoice_line_item_id")
    product = db.ReferenceField(Product, db_field="product_id")
    quantity = db.IntField(default=1)