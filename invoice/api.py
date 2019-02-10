from flask.views import MethodView
from flask import request, jsonify, abort
import uuid
from datetime import datetime

from customer.models import Customer
from cart.models import Cart
from invoice.models import Invoice
from invoice.templates import invoice_obj
from gift_card.models import GiftCard
from credit.models import Credit
from store.models import Store
from store.decorators import token_required

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
NO_OPEN_CART = "NO_CART_IS_OPEN"
INVOICE_NOT_FOUND = "INVOICE_NOT_FOUND"


class BillCartApi(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def post(self, customer_id):
        """
        bills the customers current open cart
        """

        customer = Customer.get_customer(customer_id=customer_id, request=request)
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

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

        if store.credit_order_preference == "credit":
            self.apply_credits(customer, invoice)
            self.apply_gift_cards(customer, invoice)
        else:
            self.apply_gift_cards(customer, invoice)
            self.apply_credits(customer, invoice)

        cart.state = "billed"
        cart.invoice_created_at = datetime.now()
        cart.save()

        response = {
            "result": "ok",
            "invoice": invoice_obj(invoice)
        }
        return jsonify(response), 201

    @classmethod
    def apply_gift_cards(cls, customer, invoice):
        gift_cards = GiftCard.get_active_giftcards(customer)

        while invoice.get_subtotal_amount() > 0:
            try:
                gift_card = next(gift_cards)
                gift_card.redeem(invoice)
            except StopIteration:
                return

    @classmethod
    def apply_credits(cls, customer, invoice):
        credits = Credit.get_active_credits(customer)

        while invoice.get_subtotal_amount() > 0:
            try:
                credit = next(credits)
                credit.redeem(invoice)
            except StopIteration:
                return


class InvoiceAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def get(self, invoice_id=None):
        """
        returns an invoice number or list of invoice numbers
        """
        if invoice_id:
            invoice = Invoice.objects.filter(invoice_id=invoice_id).first()
            if invoice is None:
                return jsonify({"error": INVOICE_NOT_FOUND}), 404
            response = {
                "result": "ok",
                "invoice": invoice_obj(invoice)
            }
            return jsonify(response), 200
