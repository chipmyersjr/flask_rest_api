from application import db
from datetime import datetime
import uuid

from invoice.models import Invoice, InvoiceLineItem
from credit.models import Credit


class RefundLineItem(db.EmbeddedDocument):
    refund_line_item_id = db.StringField(primary_key=True)
    invoice_line_item = db.ReferenceField(InvoiceLineItem, db_field="invoice_line_item_id")
    quantity = db.IntField(default=1)
    unit_amount_in_cents = db.IntField(default=0)
    total_amount_in_cents = db.IntField(default=0)
    tax_amount_in_cents = db.IntField(default=0)


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

    @classmethod
    def refund_invoice(cls, invoice):
        """
        refunds invoice

        :param invoice: invoice to be refunded
        :return: refund
        """

        refund = cls(
            refund_id=str(uuid.uuid4().int),
            invoice=invoice,
            cash_amount_in_cents=invoice.get_subtotal_amount()
        ).save()

        for invoice_line_item in invoice.get_invoice_line_items():
            refund.create_refund_line_item(invoice_line_item)

        return refund

    def create_refund_line_item(self, invoice_line_item):
        """
        adds a refund line item to refund

        :param invoice_line_item: invoice_line_item to be refunded
        :return: none
        """
        refund_line_item = RefundLineItem(
            refund_line_item_id=str(uuid.uuid4().int),
            invoice_line_item=invoice_line_item,
            quantity=invoice_line_item.quantity,
            unit_amount_in_cents=invoice_line_item.unit_amount_in_cents,
            total_amount_in_cents=invoice_line_item.total_amount_in_cents,
            tax_amount_in_cents=invoice_line_item.tax_amount_in_cents
        )

        self.refund_line_items.append(refund_line_item)
        self.save()
