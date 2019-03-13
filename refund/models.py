from application import db
from datetime import datetime
import uuid

from invoice.models import Invoice, InvoiceLineItem
from credit.models import Credit


class RefundLineItem(db.EmbeddedDocument):
    refund_line_item_id = db.StringField(primary_key=True)
    invoice_line_item = db.ReferenceField(InvoiceLineItem, db_field="invoice_line_item_id")
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
    def refund_invoice(cls, invoice, refund_object=None):
        """
        refunds invoice

        :param invoice: invoice to be refunded
        :param refund_object: list of objects with invoice_line_items and amounts to be refunded
        :return: refund
        """

        refund = cls(
            refund_id=str(uuid.uuid4().int),
            invoice=invoice,
            cash_amount_in_cents=invoice.get_subtotal_amount()
        ).save()

        if refund_object is None:
            invoice_line_items = invoice.get_invoice_line_items()
            for invoice_line_item in invoice_line_items:
                refund.create_refund_line_item(invoice_line_item)
        else:
            invoice_line_item_ids = [refund["invoice_line_item_id"] for refund in refund_object]
            amounts = [refund.get("amount") for refund in refund_object]
            invoice_line_items = InvoiceLineItem.objects.filter(invoice_line_item_id__in=invoice_line_item_ids
                                                                , invoice=invoice)
            for invoice_line_item in list(zip(invoice_line_items, amounts)):
                refund.create_refund_line_item(invoice_line_item[0], invoice_line_item[1])

        return refund

    def create_refund_line_item(self, invoice_line_item, amount=None):
        """
        adds a refund line item to refund

        :param invoice_line_item: invoice_line_item to be refunded
        :param amount: amount for partial refund
        :return: none
        """
        if amount:
            total_amount = amount
        else:
            total_amount = invoice_line_item.total_amount_in_cents

        refund_line_item = RefundLineItem(
            refund_line_item_id=str(uuid.uuid4().int),
            invoice_line_item=invoice_line_item,
            total_amount_in_cents=total_amount,
            tax_amount_in_cents=invoice_line_item.tax_amount_in_cents
        )

        self.refund_line_items.append(refund_line_item)
        self.save()
