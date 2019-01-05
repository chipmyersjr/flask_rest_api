from flask.views import MethodView
from flask import jsonify, request, abort
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
import uuid
from datetime import datetime


from product.models import Product
from product.schema import schema
from product.templates import product_obj, products_obj


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

        Gets a all products. Use 'page' in query string to get specific page

        Endpoint: /product/

        Example response:
        {
           "links": [
             {
               "href": "/product/?page=1",
               "rel": "self"
             },
             {
               "href": "/product/?page=2",
               "rel": "next"
             }
           ],
           "products": [
             {
               "created_at": "Tue, 01 Jan 2019 00:51:04 GMT",
               "deleted_at": null,
               "product_id": "131077205055504776670923389866612113556",
               "product_type": "Furniture",
               "title": "Bed",
               "updated_at": "Tue, 01 Jan 2019 00:51:04 GMT",
               "vendor": "Bed Co"
             },
             {
               "created_at": "Tue, 01 Jan 2019 00:52:11 GMT",
               "deleted_at": null,
               "product_id": "121476741205384160963298713726176220007",
               "product_type": "Furniture",
               "title": "Couch",
               "updated_at": "Tue, 01 Jan 2019 00:52:11 GMT",
               "vendor": "Bed Co"
             },
             {
               "created_at": "Tue, 01 Jan 2019 00:52:39 GMT",
               "deleted_at": null,
               "product_id": "323273601821423060193594938496970868250",
               "product_type": "Furniture",
               "title": "Table",
               "updated_at": "Tue, 01 Jan 2019 00:52:39 GMT",
               "vendor": "Funiture Sto"
             },

           ],
           "result": "ok"
        }
        """
        if product_id:
            product = Product.objects.filter(product_id=product_id, deleted_at=None).first()
            if product:
                response = {
                    "result": "ok",
                    "product": product_obj(product)
                }
                return jsonify(response), 200
            else:
                return jsonify({}), 404
        else:
            href = "/product/?page=%s"

            products = Product.objects.filter(deleted_at=None)

            page = int(request.args.get('page', 1))
            products = products.paginate(page=page, per_page=self.PER_PAGE)

            response = {
                "result": "ok",
                "links": [
                    {
                        "href": href % page,
                        "rel": "self"
                    }
                ],
                "products": products_obj(products)
            }
            if products.has_prev:
                response["links"].append(
                    {
                        "href": href % products.prev_num,
                        "rel": "previous"
                    }
                )
            if products.has_next:
                response["links"].append(
                    {
                        "href": href % products.next_num,
                        "rel": "next"
                    }
                )
            return jsonify(response), 200

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

    def put(self, product_id):
        """
        update a specific product

        Endpoint: /product/88517737685737189039085760589870132011

        Example Body:
            {
                "title": "Kitty Litter",
                "product_type": "Pets",
                "vendor": "Pet Co"
            }
        """
        product = Product.objects.filter(product_id=product_id, deleted_at=None).first()
        if not product:
            return jsonify({}), 404

        product_json = request.json
        error = best_match(Draft4Validator(schema).iter_errors(product_json))
        if error:
            return jsonify({"error": error.message}), 400

        product.title = product_json.get("title")
        product.product_type = product_json.get("product_type")
        product.vendor = product_json.get("vendor")
        product.updated_at = datetime.utcnow()
        product.save()

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


class ProductCountAPI(MethodView):

    def get(self):
        """
        Returns a count of all products

        Endpoint = /product/count/

        Example response:
        {
          "count": "20",
          "result": "ok"
        }
        """
        response = {
                      "result": "ok",
                      "count": str(Product.objects.count())
                   }

        return jsonify(response), 200
