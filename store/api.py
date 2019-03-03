from flask import request, abort, jsonify, current_app
from flask.views import MethodView
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
from datetime import datetime

from store.schema import schema, token_request_schema
from store.models import Store, AccessToken
from store.templates import store_obj
from store.decorators import token_required

CREDIT_ORDER_PREFERENCE_ERROR = "CREDIT_ORDER_ALLOWED_VALUES_ARE_CREDIT_GIFT-CARD"


class StoreAPI(MethodView):

    def __init__(self):
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @classmethod
    @token_required
    def get(cls):
        """
        returns info on the current store. Store is determined by app-id provided in header

        Endpoint = /store/

        Example response:
        {
            "result": "ok",
            "store": {
                "created_at": "Sat, 05 Jan 2019 22:21:54 GMT",
                "deleted_at": null,
                "links": [
                    {
                        "href": "/store/296194664480373992904103034340308325889",
                        "rel": "self"
                    }
                ],
                "name": "Food Store",
                "store_id": "296194664480373992904103034340308325889",
                "tagline": "Yummmmmm",
                "updated_at": "Sat, 05 Jan 2019 22:21:54 GMT"
            }
        }
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()
        if store:
            response = {
                "result": "ok",
                "store": store_obj(store)
            }
            return jsonify(response), 200

    @classmethod
    def post(cls):
        """
        Creates a new store

        Endpoint: /store/

        Example Post Body:
        {
            "name": "Electronics Store",
            "tagline": "A really good electronics store",
            "app_id": "my_electronics_app",
            "app_secret": "my_electronics_secret"
        }

        Example Response:
        {
            "result": "ok",
            "store": {
                "created_at": "Sat, 05 Jan 2019 21:11:30 GMT",
                "deleted_at": null,
                "links": [
                    {
                        "href": "/store/241787390524523237447764623791517213747",
                        "rel": "self"
                    }
                ],
                "name": "Electronics Store",
                "store_id": "241787390524523237447764623791517213747",
                "tagline": "A really good electronics store",
                "updated_at": "Sat, 05 Jan 2019 21:11:30 GMT"
            }
        }
        """
        store_json = request.json
        error = best_match(Draft4Validator(schema).iter_errors(store_json))
        if error:
            return jsonify({"error": error.message}), 400

        store = Store.objects.filter(app_id=store_json.get("app_id")).first()
        if store:
            return jsonify({"error": "APP_ID_ALREADY_EXISTS"}), 400

        if store_json.get("credit_order_preference"):
            if store_json.get("credit_order_preference").lower() not in ["credit", "gift-card"]:
                return jsonify({"error": CREDIT_ORDER_PREFERENCE_ERROR}), 400

        store = Store(
            name=store_json.get("name"),
            tagline=store_json.get("tagline"),
            app_id=store_json.get("app_id"),
            app_secret=store_json.get("app_secret")
        ).save()

        if store_json.get("credit_order_preference"):
            store.credit_order_preference = store_json.get("credit_order_preference")
            store.save()

        response = {
            "result": "ok",
            "store": store_obj(store)
        }
        return jsonify(response), 201

    @classmethod
    @token_required
    def put(cls):
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        request_json = request.json
        name = request_json.get("name")
        tagline = request_json.get("tagline")
        credit_order_preference = request_json.get("credit_order_preference")

        if name is None and tagline is None and credit_order_preference is None:
            return jsonify({"error": "No fields to update were supplied"}), 400

        if name:
            store.name = name
        if tagline:
            store.tagline = tagline
        if credit_order_preference:
            if credit_order_preference.lower() not in ['credit', 'gift-card']:
                return jsonify({"error": CREDIT_ORDER_PREFERENCE_ERROR}), 400
            store.credit_order_preference = credit_order_preference
        store.updated_at = datetime.now()
        store.save()

        response = {
            "result": "ok",
            "store": store_obj(store)
        }
        return jsonify(response), 201

    @classmethod
    def delete(cls):
        """
        deletes the current store based on the app-id header

        Endpoint: /store/
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()
        if not store:
            return jsonify({}), 404
        store.deleted_at = datetime.now()
        store.save()

        return jsonify({}), 204


class StoreTokenAPI(MethodView):

    def __init__(self):
        if request.method != 'POST' or not request.json:
            abort(400)

    @classmethod
    def post(cls):
        """
        Creates a token for a given app_id that expires in 24 hours.  The token will be passed in the headers as the
        authentication method.

        Endpoint = /store/token/

        Example Post Body:
        {
            "app_id": "my_electronics_app",
            "app_secret": "my_electronics_secret"
        }

        Example Response:
        {
            "expires_at": "Sun, 06 Jan 2019 21:15:49 GMT",
             "token": "303137304782462606160050118190185819344"
        }

        """
        request_json = request.json
        error = best_match(Draft4Validator(token_request_schema).iter_errors(request_json))
        if error:
            return jsonify({"error": error.message}), 400

        store = Store.objects.filter(app_id=request_json.get("app_id"), deleted_at=None).first()

        if not store:
            return jsonify({'error': "APP_ID NOT FOUND"}), 400

        if request.json.get('app_secret') != store.app_secret:
            return jsonify({'error': "APP_SECRET IS INCORRECT"}), 400

        AccessToken.objects.filter(store_id=store).delete()

        token = AccessToken(
                store_id=store
        ).save()

        return jsonify({'token': token.token, 'expires_at': token.expires_at}), 201

