from application import db
from datetime import datetime

from customer.models import Customer
from invoice.models import Invoice


class GiftCard(db.Document):
    gift_card_id = db.StringField(db_field="gift_card_id", primary_key=True)
    gifter_customer = db.ReferenceField(Customer, db_field="gifter_customer_id")
    recipient_customer = db.ReferenceField(Customer, db_field="recipient_customer_id")
    original_balance_in_cents = db.IntField()
    current_balance_in_cents = db.IntField()
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField()


class GiftCardSpend(db.Document):
    gift_card_spend_id = db.StringField(db_field="gift_card_spend_id", primary_key=True)
    gift_card = db.ReferenceField(GiftCard, db_field="gift_card_id")
    invoice = db.ReferenceField(Invoice, db_field="invoice_id")
    amount = db.DecimalField()
    remaining_balance = db.DecimalField()
    created_at = db.DateTimeField(default=datetime.now())