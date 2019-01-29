from application import db
from datetime import datetime

from customer.models import Customer

# gift_card_spend_id
# gift_card_id
# invoice_id
# amount
# remaining_balance
# created_at
class GiftCard(db.Document):
    gift_card_id = db.StringField(db_field="gift_card_id", primary_key=True)
    gifter_customer = db.ReferenceField(Customer, db_field="gift_card_id")
    recipient_customer = db.ReferenceField(Customer, db_field="recipient_customer_id")
    original_balance = db.DecimalField()
    current_balance = db.DecimalField()
    created_at = db.DateTimeField(default=datetime.now())
    updated = db.DateTimeField()


class GiftCardSpend(db.Document):
    gift_card_spend_id = db.StringField(db_field="gift_card_spend_id", primary_key=True)
    gift_card = db.ReferencField(GiftCard)
    amount = db.DecimalField()
    remaining_balance = db.DecimalField()
    created_at = db.DateTimeField(default=datetime.now())