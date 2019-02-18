from application import db
from datetime import datetime
import uuid

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
    voided_at = db.DateTimeField()

    def redeem(self, invoice):
        amount_to_apply = min([invoice.get_subtotal_amount(), self.current_balance_in_cents])

        invoice.gift_card_used_amount_in_cents += amount_to_apply
        invoice.save()

        GiftCardSpend(
            gift_card_spend_id=str(uuid.uuid4().int),
            gift_card=self,
            invoice=invoice,
            amount=amount_to_apply,
            remaining_balance=self.current_balance_in_cents - amount_to_apply
        ).save()

        self.current_balance_in_cents -= amount_to_apply
        self.updated_at = datetime.now()
        self.save()

    @classmethod
    def get_active_giftcards(cls, customer):
        gift_cards = GiftCard.objects.filter(recipient_customer=customer, current_balance_in_cents__gt=0).all()

        for gift_card in gift_cards:
            yield gift_card

    def void(self):
        self.voided_at = datetime.now()
        self.updated_at = datetime.now()
        self.current_balance_in_cents = 0
        self.save()


class GiftCardSpend(db.Document):
    gift_card_spend_id = db.StringField(db_field="gift_card_spend_id", primary_key=True)
    gift_card = db.ReferenceField(GiftCard, db_field="gift_card_id")
    invoice = db.ReferenceField(Invoice, db_field="invoice_id")
    amount = db.DecimalField()
    remaining_balance = db.DecimalField()
    created_at = db.DateTimeField(default=datetime.now())