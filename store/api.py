from flask import request, abort, jsonify
from flask.views import MethodView
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match

from store.schema import schema
from store.models import Store
from store.templates import store_obj


class StoreAPI(MethodView):

    def __init__(self):
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def post(self):
        product_json = request.json
        error = best_match(Draft4Validator(schema).iter_errors(product_json))
        if error:
            return jsonify({"error": error.message}), 400

        store = Store(
            name=product_json.get("name"),
            tagline=product_json.get("tagline"),
            app_id=product_json.get("app_id"),
            app_secret=product_json.get("app_secret")
        ).save()

        response = {
            "result": "ok",
            "store": store_obj(store)
        }
        return jsonify(response), 201