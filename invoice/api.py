from flask.views import MethodView
from flask import request, jsonify, abort
import uuid

from customer.models import Customer
from cart.models import Cart
from invoice.models import Invoice
from invoice.templates import invoice_obj

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
NO_OPEN_CART = "NO_CART_IS_OPEN"


class BillCartApi(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def post(self, customer_id):
        """
        bills the customers current open cart
        """

        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        cart = Cart.objects.filter(customer_id=customer_id, invoice_created_at=None, closed_at=None).first()

        if cart is None:
            return jsonify({"error": NO_OPEN_CART}), 404

        invoice = Invoice(
            invoice_id=str(uuid.uuid4().int),
            customer=customer,
            cart=cart
        ).save()

        invoice.create_invoice_line_items()

        response = {
            "result": "ok",
            "invoice": invoice_obj(invoice)
        }
        return jsonify(response), 201
