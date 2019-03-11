from flask.views import MethodView
from flask import request, jsonify, abort

from store.decorators import token_required
from store.models import Store
from invoice.models import Invoice
from refund.models import Refund
from refund.templates import refund_object

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
INVOICE_NOT_FOUND = "INVOICE_NOT_FOUND"


class RefundAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def post(self, invoice_id):
        """
        refunds invoice

        query_param full: refunds entire invoice if true

        :param invoice_id: invoice to be refunded
        :return:
        """
        invoice = Invoice.objects.filter(invoice_id=invoice_id, state='collected').first()
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        if invoice is None:
            return jsonify({"error": INVOICE_NOT_FOUND}), 404

        if invoice.customer.store_id != store:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        refund = Refund.refund_invoice(invoice)

        response = {
            "result": "ok",
            "invoice": refund_object(refund)
        }
        return jsonify(response), 201