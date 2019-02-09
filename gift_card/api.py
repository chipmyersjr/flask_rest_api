from flask.views import MethodView
from flask import request, jsonify, abort
from datetime import datetime
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
import uuid

from gift_card.models import GiftCard
from gift_card.schema import create_gift_cart_schema
from gift_card.templates import gift_card_obj, gift_card_objs
from store.models import Store
from store.decorators import token_required
from customer.models import Customer
from utils import paginated_results

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
MISSING_PARAMETERS = "MISSING_PARAMETERS"


class GiftCardAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def get(self, gift_card_id=None):
        """
        returns a gift_card object of list of gift_card objects
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        if gift_card_id:
            gift_card = GiftCard.objects.filter(gift_card_id=gift_card_id).first()

            if gift_card is None:
                return jsonify({}), 404

            if gift_card.recipient_customer.store_id != store:
                return jsonify({}), 404

            response = {
                "result": "ok",
                "gift_card": gift_card_obj(gift_card)
            }
            return jsonify(response), 200
        else:
            gift_cards = GiftCard.objects()

            if "giftercustomerid" not in request.args and "recipientcustomerid" not in request.args:
                return jsonify({"error": MISSING_PARAMETERS}), 400

            if "giftercustomerid" in request.args:
                gifter_customer = Customer.objects.filter(customer_id=request.args['giftercustomerid'], store_id=store
                                                          , deleted_at=None).first()
                if gifter_customer is None:
                    return jsonify({"error": CUSTOMER_NOT_FOUND}), 404
                gift_cards = gift_cards.filter(gifter_customer=gifter_customer)

            if "recipientcustomerid" in request.args:
                recipient_customer = Customer.objects.filter(customer_id=request.args['recipientcustomerid']
                                                             , store_id=store, deleted_at=None).first()

                if recipient_customer is None:
                    return jsonify({"error": CUSTOMER_NOT_FOUND}), 404
                gift_cards = gift_cards.filter(recipient_customer=recipient_customer)

            if "active" in request.args:
                if request.args['active'].lower() == 'true':
                    gift_cards = gift_cards.filter(current_balance_in_cents__gt=0)

            return paginated_results(objects=gift_cards, collection_name='gift_card', request=request
                                     , per_page=self.PER_PAGE, serialization_func=gift_card_objs), 200

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


class CustomerGiftCardAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def get(self, customer_id):
        """
        returns a list of customer gift cards
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        customer = Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        gift_cards = GiftCard.objects.filter(recipient_customer=customer)

        if "active" in request.args:
            if request.args['active'].lower() == 'true':
                gift_cards = gift_cards.filter(current_balance_in_cents__gt=0)

        return paginated_results(objects=gift_cards, collection_name='gift_card', request=request
                                 , per_page=self.PER_PAGE, serialization_func=gift_card_objs), 200