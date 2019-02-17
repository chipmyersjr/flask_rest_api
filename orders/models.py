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

    @classmethod
    def create_order(cls, invoice):
        """
        creates a new order

        :param invoice: customer invoice to be fulfilled
        :return: order object
        """
        order = cls(
            order_id=str(uuid.uuid4().int),
            invoice=invoice
        ).save()

        invoice_line_items = InvoiceLineItem.objects.filter(invoice=invoice, type="item").all()

        for invoice_line_item in invoice_line_items:
            OrderLineItem.create_order_line_item(order=order, invoice_line_item=invoice_line_item)

        return order


class OrderLineItem(db.Document):
    order_line_item_id = db.StringField(order_line_item_id="invoice_id", primary_key=True)
    order = db.ReferenceField(Order, db_field="order_id")
    invoice_line_item = db.ReferenceField(InvoiceLineItem, db_field="invoice_line_item_id")
    product = db.ReferenceField(Product, db_field="product_id")
    quantity = db.IntField(default=1)

    @classmethod
    def create_order_line_item(cls, order, invoice_line_item):
        """
        create one order line item

        :param order: order to be included in
        :param invoice_line_item: invoice line item to be added to order
        :return: order line item object
        """
        order_line_item = cls(
            order_line_item_id=str(uuid.uuid4().int),
            order=order,
            invoice_line_item=invoice_line_item,
            product=invoice_line_item.product,
            quantity=invoice_line_item.quantity
        ).save()

        return order_line_item