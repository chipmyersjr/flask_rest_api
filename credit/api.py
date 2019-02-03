from flask.views import MethodView
from flask import request, jsonify, abort
import uuid

from store.decorators import token_required
from store.models import Store
from customer.models import Customer
from credit.models import Credit
from credit.templates import credit_obj

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
AMOUNT_SHOULD_BE_INT = "AMOUNT_SHOULD_BE_INT"


class CustomerCreditAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def post(self, customer_id, amount):
        """
        issue a credit to a customer

        :param customer_id: customer to add credit to
        :param amount: amount of credit to be given
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        customer = Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        try:
            amount = int(amount)
        except ValueError:
            return jsonify({"error": AMOUNT_SHOULD_BE_INT}), 400

        credit = Credit(
            credit_id=str(uuid.uuid4().int),
            customer=customer,
            original_balance_in_cents=amount,
            current_balance_in_cents=amount
        ).save()

        response = {
            "result": "ok",
            "credit": credit_obj(credit)
        }
        return jsonify(response), 201
