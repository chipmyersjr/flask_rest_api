from flask.views import MethodView
from flask import jsonify, request, abort
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
import uuid


from product.models import Product
from product.schema import schema
from product.templates import product_obj


class ProductAPI(MethodView):

    def __init__(self):
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def post(self):
        product_json = request.json
        error = best_match(Draft4Validator(schema).iter_errors(product_json))
        if error:
            return jsonify({"error": error.message}), 400

        product = Product(
            id=str(uuid.uuid4()),
            title=product_json.get("title"),
            product_type=product_json.get("product_type"),
            vendor=product_json.get("product_type")
        ).save()

        response = {
            "result": "ok",
            "product": product_obj(product)
        }
        return jsonify(response), 201
