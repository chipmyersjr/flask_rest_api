from application import db
from datetime import datetime
import uuid

from customer.models import Customer
from cart.models import Cart
from cart.models import CartItem
from product.models import Product


class Invoice(db.Document):
    invoice_id = db.StringField(db_field="invoice_id", primary_key=True)
    customer = db.ReferenceField(Customer, db_field="customer_id")
    cart = db.ReferenceField(Cart, db_field="cart_id")
    state = db.StringField(default="open")
    gift_card_used_amount_in_cents = db.IntField(default=0)
    credit_used_amount_in_cents = db.IntField(default=0)
    created_at = db.DateTimeField(default=datetime.now())
    closed_at = db.DateTimeField()

    meta = {
        'indexes': [('customer', ), ('cart', )]
    }

    def create_invoice_line_items(self):
        invoice_line_items = []
        for cart_item in self.cart.get_cart_items():
            invoice_line_item = InvoiceLineItem(
                                    invoice_line_item_id=str(uuid.uuid4().int),
                                    invoice=self,
                                    cart_item=cart_item,
                                    product=cart_item.product_id,
                                    quantity=cart_item.quantity,
                                    unit_amount_in_cents=cart_item.product_id.sale_price_in_cents,
                                    total_amount_in_cents=cart_item.product_id.sale_price_in_cents*cart_item.quantity,
                                    type="item"
                                )
            invoice_line_items.append(invoice_line_item)
            invoice_line_item.invoice_created_at = datetime.now()
            invoice_line_item.save()

        return invoice_line_items

    def get_total_amount(self):
        invoice_line_items = InvoiceLineItem.objects.filter(invoice=self).all()
        return sum([invoice_line_item.total_amount_in_cents for invoice_line_item in invoice_line_items])

    def get_tax_amount(self):
        invoice_line_items = InvoiceLineItem.objects.filter(invoice=self).all()
        return sum([invoice_line_item.tax_amount_in_cents for invoice_line_item in invoice_line_items])

    def get_subtotal_amount(self):
        return self.get_total_amount() - self.gift_card_used_amount_in_cents - self.credit_used_amount_in_cents \
              + self.get_tax_amount()


class InvoiceLineItem(db.Document):
    invoice_line_item_id = db.StringField(db_field="invoice_line_item_id", primary_key=True)
    invoice = db.ReferenceField(Invoice, db_field="invoice_id")
    cart_item = db.ReferenceField(CartItem, db_field="cart_item_id")
    product = db.ReferenceField(Product, db_field="product_id")
    quantity = db.IntField()
    unit_amount_in_cents = db.IntField()
    total_amount_in_cents = db.IntField()
    tax_amount_in_cents = db.IntField(default=0)
    type = db.StringField()

    meta = {
        'indexes': [('invoice',)]
    }