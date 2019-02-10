from application import db
from datetime import datetime

from customer.models import Customer
from invoice.models import Invoice


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

    def redeem(self, invoice):
        amount_to_apply = min([invoice.get_subtotal_amount(), self.current_balance_in_cents])

        invoice.credit_used_amount_in_cents += amount_to_apply
        invoice.updated_at = datetime.now()
        invoice.save()

        self.current_balance_in_cents -= amount_to_apply
        self.updated_at = datetime.now()
        self.save()

    @classmethod
    def get_active_credits(cls, customer):
        credits = Credit.objects.filter(customer=customer, current_balance_in_cents__gt=0).all()

        for credit in credits:
            yield credit


class CreditRedemption(db.Document):
    credit_redemption_id = db.StringField(db_field="credit_redemption_id", primary_key=True)
    credit = db.ReferenceField(Credit, db_field="credit_id")
    invoice = db.ReferenceField(Invoice, db_field="invoice_id")
    amount = db.IntField()
    remaining_balance = db.IntField()
    created_at = db.DateTimeField(default=datetime.now())