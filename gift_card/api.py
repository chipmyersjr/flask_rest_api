from flask.views import MethodView
from flask import request, jsonify, abort
from datetime import datetime
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
import uuid

from gift_card.models import GiftCard
from gift_card.schema import create_gift_cart_schema
from gift_card.templates import gift_card_obj
from store.models import Store
from store.decorators import token_required
from customer.models import Customer

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"


class GiftCardAPI(MethodView):

    def __init__(self):
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def post(self):
        """
        creates a new gift card.
        """
        error = best_match(Draft4Validator(create_gift_cart_schema).iter_errors(request.json))
        if error:
            return jsonify({"error": error.message}), 400

        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        gifter_customer = Customer.objects.filter(customer_id=request.json.get("gifter_customer_id")
                                           , store_id=store, deleted_at=None).first()
        if gifter_customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        recipient_customer = Customer.objects.filter(customer_id=request.json.get("recipient_customer_id")
                                                     , store_id=store, deleted_at=None).first()
        if recipient_customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        gift_card = GiftCard(
            gift_card_id=str(uuid.uuid4().int),
            gifter_customer=gifter_customer,
            recipient_customer=recipient_customer,
            original_balance_in_cents=request.json.get("original_amount"),
            current_balance_in_cents=request.json.get("original_amount")
        ).save()

        response = {
            "result": "ok",
            "gift_card": gift_card_obj(gift_card)
        }
        return jsonify(response), 201