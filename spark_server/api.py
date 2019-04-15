from flask.views import MethodView
from flask import request, jsonify, abort
import json

from utils import get_redis_connection
from store.decorators import token_required
from store.models import Store
from product.models import Product
from product.templates import products_obj

TOP_TEN_CART_ITEMS = "Store_Product_Count"
INVOICE_AMOUNT = "Invoice_Amount"


class TopTenCartItemsAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def get(self, n=10):
        """
        returns the top ten products added to customer carts
        """
        try:
            N = int(n)
        except ValueError:
            return jsonify({"error": "N shoud be integer"})

        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        redis_conn = get_redis_connection()

        response = json.loads(redis_conn.get(TOP_TEN_CART_ITEMS))

        product_ids = {}
        counter = 0
        for key, value in sorted(response.items(), key=lambda x: x[1], reverse=True):
            split_values = key.split("|")
            if split_values[1] == store.store_id:
                product_ids[split_values[0]] = value
            counter += 1
            if counter == N:
                break

        products = Product.objects.filter(product_id__in=product_ids.keys())

        products = products.paginate(page=1, per_page=N)

        response = {
            "result": "ok",
            "products": products_obj(products)
        }

        for product in response["products"]:
            for key, value in product_ids.items():
                if product["product_id"] == key:
                    product["number_of_cart_adds"] = value

        response["products"] = sorted(response["products"]
                                      , key=lambda product: product["number_of_cart_adds"], reverse=True)

        return jsonify(response), 200


class InvoiceAmountAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def get(self):
        """
        return the total invoiced amount in the last two hours
        """

        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        redis_conn = get_redis_connection()

        redis_response = json.loads(redis_conn.get(INVOICE_AMOUNT))

        try:
            result = redis_response[store.store_id]
        except KeyError:
            result = 0

        response = {
            "result": result
        }

        return jsonify(response), 200
