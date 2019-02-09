from application import db
from datetime import datetime

from customer.models import Customer


class Credit(db.Document):
    credit_id = db.StringField(db_field="credit_id", primary_key=True)
    customer = db.ReferenceField(Customer, db_field="customer_id")
    original_balance_in_cents = db.IntField()
    current_balance_in_cents = db.IntField()
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField()
    voided_at = db.DateTimeField()

    def void_credit(self):
        self.voided_at = datetime.now()
        self.updated_at = datetime.now()
        self.current_balance_in_cents = 0
        self.save()


class CreditRedemption(db.Document):
    credit_redemption_id = db.StringField(db_field="credit_redemption_id", primary_key=True)
    credit = db.ReferenceField(Credit, db_field="credit_id")
    amount = db.IntField()
    remaining_balance = db.IntField()
    created_at = db.DateTimeField(default=datetime.now())