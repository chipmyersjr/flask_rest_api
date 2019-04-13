from flask.views import MethodView
from flask import request, jsonify, abort
import uuid
from datetime import datetime
from mongoengine.errors import NotUniqueError

from customer.models import Customer
from cart.models import Cart
from invoice.models import Invoice, IncorrectDateFormat, CouponCode
from invoice.templates import invoice_obj, invoice_objs
from gift_card.models import GiftCard
from credit.models import Credit
from store.models import Store
from store.decorators import token_required
from orders.models import Order
from orders.templates import order_obj
from utils import paginated_results

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
NO_OPEN_CART = "NO_CART_IS_OPEN"
INVOICE_NOT_FOUND = "INVOICE_NOT_FOUND"
INCORRECT_TIME_FORMAT = "INCORRECT_TIME_FORMAT"
INVOICE_IS_NOT_OPEN = "INVOICE_IS_NOT_OPEN"


class BillCartApi(MethodView):
    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def post(self, customer_id):
        """
        bills the customers current open cart

        --Bills the current open cart for customer
        --Create Invoice Record and Invoice Line Item Records
        --Automatically applies giftcard and credits
        --closes cart as 'billed'
        --store.credit_order_preference: determines if credits are giftcards are applied first
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

        if "coupon" in request.args:
            coupon = CouponCode.objects.filter(code=request.args.get("coupon"), store=store).first()
            if coupon is None:
                return jsonify({"error": "coupon code not found"}), 404

            redemption = coupon.redeem(invoice=invoice)

            if redemption is None:
                return jsonify({"error": "coupon code not found"}), 404

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

        params:
        closed: true if want to include closed invoices
        startdate: date range filter
        enddate: date range filter
        """
        if invoice_id:
            invoice = Invoice.objects.filter(invoice_id=invoice_id).first()
            store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

            if invoice is None:
                return jsonify({"error": INVOICE_NOT_FOUND}), 404

            if invoice.customer.store_id != store:
                return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

            response = {
                "result": "ok",
                "invoice": invoice_obj(invoice)
            }
            return jsonify(response), 200
        else:
            try:
                invoices = Invoice.get_all_invoices(request=request)
            except IncorrectDateFormat:
                return jsonify({"error": INCORRECT_TIME_FORMAT})

            return paginated_results(objects=invoices, collection_name='invoice', request=request
                                     , per_page=self.PER_PAGE, serialization_func=invoice_objs), 200


class InvoiceCollectedAPI(MethodView):
    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def post(self, invoice_id):
        invoice = Invoice.objects.filter(invoice_id=invoice_id).first()
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        if invoice.customer.store_id != store:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        if invoice is None:
            return jsonify({"error": INVOICE_NOT_FOUND}), 404

        if invoice.state != 'open':
            return jsonify({"error": INVOICE_IS_NOT_OPEN}), 400

        invoice.state = "collected"
        invoice.closed_at = datetime.now()
        invoice.customer.last_order_date = datetime.now()
        invoice.customer.total_spent += invoice.get_pre_tax_amount()
        invoice.customer.save()
        invoice.save()

        order = Order.create_order(invoice=invoice)

        response = {
            "result": "ok",
            "order": order_obj(order)
        }

        return jsonify(response), 201


class InvoiceFailedAPI(MethodView):
    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def put(self, invoice_id):
        invoice = Invoice.objects.filter(invoice_id=invoice_id).first()
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        if invoice.customer.store_id != store:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        if invoice is None:
            return jsonify({"error": INVOICE_NOT_FOUND}), 404

        if invoice.state != 'open':
            return jsonify({"error": INVOICE_IS_NOT_OPEN}), 400

        invoice.state = "failed"
        invoice.closed_at = datetime.now()
        invoice.save()

        response = {
            "result": "ok",
            "invoice": invoice_obj(invoice)
        }
        return jsonify(response), 200


class CustomerInvoiceAPI(MethodView):
    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def get(self, customer_id):
        """
        return a list of invoice for customer

        params:
        closed: true if want to include closed invoices
        startdate: date range filter
        enddate: date range filter
        """
        try:
            invoices = Invoice.get_all_invoices(request=request)
        except IncorrectDateFormat:
            return jsonify({"error": INCORRECT_TIME_FORMAT})

        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        invoices = invoices.filter(customer=customer_id)

        return paginated_results(objects=invoices, collection_name='invoice', request=request
                                 , per_page=self.PER_PAGE, serialization_func=invoice_objs), 200


class CouponCodeAPI(MethodView):
    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def post(self):
        """
        creates a new coupon code

        :return: coupon code object
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        if "code" in request.args:
            code = request.args.get("code")
        else:
            return jsonify({"error": "Please provide coupon code as query param 'code'"}), 400

        if "amount" in request.args:
            try:
                amount = int(request.args.get("amount"))
            except ValueError:
                return jsonify({"error": "Amount should be integer"}), 400
        else:
            return jsonify({"error": "Please provide amount as query param 'amount'"}), 400

        if amount < 0:
            return jsonify({"error": "Invalid Amount"}), 400

        style = request.args.get("style", "dollars_off")

        if "expires_at" in request.args:
            try:
                expires_at = datetime.strptime(request.args.get("expires_at"), "%Y%m%d%H")
            except ValueError:
                return jsonify({"error": "incorrect date format"}), 400
        else:
            expires_at = None

        if style not in ["dollars_off", "percent_off"]:
            return jsonify({"error": "Style type does not exist"}), 400

        if style == "percent_off":
            if amount > 100:
                return jsonify({"error": "Invalid amount For style percent off"}), 400

        try:
            coupon = CouponCode(
                coupon_code_id=str(uuid.uuid4().int),
                store=store,
                code=code,
                style=style,
                amount=amount,
                expires_at=expires_at
            ).save()
        except NotUniqueError:
            return jsonify({"error": "coupon code already exists"}), 400

        response = {
            "result": "ok",
            "coupon": coupon.to_dict()
        }
        return jsonify(response), 201

    @token_required
    def get(self, code):
        """
        true if coupon code is valid

        :return: coupon code object
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        coupon = CouponCode.objects.filter(code=code, store=store).first()

        if coupon is None:
            return jsonify({"error": "not found"}), 404

        response = {
            "result": coupon.is_valid(),
            "coupon": coupon.to_dict()
        }
        return jsonify(response), 200

    @token_required
    def delete(self, code):
        """
        voids coupon

        :param code: coupon to void
        :return: null
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        coupon = CouponCode.objects.filter(code=code, store=store).first()

        if coupon is None:
            return jsonify({"error": "not found"}), 404

        coupon.voided_at = datetime.now()
        coupon.save()

        return jsonify({}), 204