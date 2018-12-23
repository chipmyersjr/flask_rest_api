from flask.views import MethodView
from flask import jsonify, request, abort
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
import uuid
from datetime import datetime


from product.models import Product
from product.schema import schema
from product.templates import product_obj


class ProductAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def get(self, product_id=None):
        """
        Gets a product by providing product_id

        Endpoint: /product/242025312983347096410127212123600214518

        Example response:
        {
        "pet": {
             "created_at": "Sun, 23 Dec 2018 00:34:16 GMT",
             "product_id": "242025312983347096410127212123600214518",
             "product_type": "Furniture",
             "title": "Table",
             "updated_at": "Sun, 23 Dec 2018 00:34:16 GMT",
             "vendor": "Furniture"
        },
        "result": "ok"
        }
        """
        if product_id:
            product = Product.objects.filter(product_id=product_id, deleted_at=None).first()
            if product:
                response = {
                    "result": "ok",
                    "pet": product_obj(product)
                }
                return jsonify(response), 200
            else:
                return jsonify({}), 404

    def post(self):
        """
        Creates a new product.

        Endpoint: /product/

        Example Post Body:
        {
            "title": "PS4",
            "product_type": "Electronics",
            "vendor": "Sony"
        }

        Example response:
        {
            "product": {
                    "created_at": "Sat, 22 Dec 2018 22:45:50 GMT",
                    "id": "ef5a799c-7f43-412e-89a3-ed666f605482",
                    "product_type": "Electronics",
                    "title": "PS4",
                    "updated_at": "Sat, 22 Dec 2018 22:45:50 GMT",
                    "vendor": "Electronics"
                        },
                "result": "ok"
        }
        """
        product_json = request.json
        error = best_match(Draft4Validator(schema).iter_errors(product_json))
        if error:
            return jsonify({"error": error.message}), 400

        print("ok")
        product = Product(
            product_id=str(uuid.uuid4().int),
            title=product_json.get("title"),
            product_type=product_json.get("product_type"),
            vendor=product_json.get("vendor")
        ).save()

        response = {
            "result": "ok",
            "product": product_obj(product)
        }
        return jsonify(response), 201

    def delete(self, product_id):
        """
        delete a specific product by providing product id

        Endpoint: /product/88517737685737189039085760589870132011
        """
        product = Product.objects.filter(product_id=product_id, deleted_at=None).first()
        if not product:
            return jsonify({}), 404
        product.deleted_at = datetime.utcnow()
        product.save()

        return jsonify({}), 204
