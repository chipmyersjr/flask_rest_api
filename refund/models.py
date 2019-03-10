from application import db
from datetime import datetime

from invoice.models import Invoice, InvoiceLineItem
from credit.models import Credit


class RefundLineItem(db.EmbeddedDocument):
    refund_line_item_id = db.StringField(primary_key=True)
    invoice_line_item = db.ReferenceField(InvoiceLineItem, db_field="invoice_line_item_id")
    quantity = db.IntField(default=1)
    unit_amount = db.IntField(default=0)
    total_amount = db.IntField(default=0)
    tax_amount = db.IntField(default=0)


class Refund(db.Document):
    refund_id = db.StringField(primary_key=True)
    invoice = db.ReferenceField(Invoice, db_field="invoice_id")
    credit = db.ReferenceField(Credit, db_field="credit_id")
    cash_amount_in_cents = db.IntField(default=0)
    credit_amount_in_cents = db.IntField(default=0)
    state = db.StringField(default="open")
    refund_line_items = db.ListField(db.EmbeddedDocumentField(RefundLineItem))
    created_at = db.DateTimeField(default=datetime.now())
    closed_at = db.DateTimeField()