from flask import request, abort, jsonify
from flask.views import MethodView
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
import uuid

from store.schema import schema, token_request_schema
from store.models import Store, AccessToken
from store.templates import store_obj


class StoreAPI(MethodView):

    def __init__(self):
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def post(self):
        store_json = request.json
        error = best_match(Draft4Validator(schema).iter_errors(store_json))
        if error:
            return jsonify({"error": error.message}), 400

        store = Store(
            name=store_json.get("name"),
            tagline=store_json.get("tagline"),
            app_id=store_json.get("app_id"),
            app_secret=store_json.get("app_secret")
        ).save()

        response = {
            "result": "ok",
            "store": store_obj(store)
        }
        return jsonify(response), 201


class StoreTokenAPI(MethodView):

    def __init__(self):
        if request.method != 'POST' or not request.json:
            abort(400)

    def post(self):
        request_json = request.json
        error = best_match(Draft4Validator(token_request_schema).iter_errors(request_json))
        if error:
            return jsonify({"error": error.message}), 400

        store = Store.objects.filter(app_id=request_json.get("app_id")).first()

        if not store:
            return jsonify({'error': "APP_ID NOT FOUND"}), 400

        if request.json.get('app_secret') != store.app_secret:
            return jsonify({'error': "APP_SECRET IS INCORRECT"}), 400

        AccessToken.objects.filter(store_id=store).delete()

        token = AccessToken(
                store_id=store
        ).save()

        return jsonify({'token': token.token, 'expires_at': token.expires_at}), 201

