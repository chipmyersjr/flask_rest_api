from flask.views import MethodView
from flask import request, jsonify, abort
import json

from utils import get_redis_connection
from store.decorators import token_required
from store.models import Store
from product.models import Product
from product.templates import products_obj
from invoice.models import CouponCode

TOP_TEN_CART_ITEMS = "Store_Product_Count"
INVOICE_AMOUNT = "Invoice_Amount"
TOP_COUPON = "Top_Coupon_Code"
NEW_CUSTOMERS = "New_Customers"
CUSTOMER_LOGINS = "Customer_Logins"


def results_by_store_id(request, topic_name):
    """
    helper function to return a redis cached result by store_id

    :param request: flask request object
    :return: response object
    """
    store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

    redis_conn = get_redis_connection()

    redis_response = json.loads(redis_conn.get(topic_name))

    try:
        result = redis_response[store.store_id]
    except KeyError:
        result = 0

    return {"result": result}


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

        response = results_by_store_id(request, INVOICE_AMOUNT)

        return jsonify(response), 200


class TopCouponCode(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def get(self):
        """
        returns the most used coupon code in last two hours

        :return: coupon code object
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        redis_conn = get_redis_connection()

        redis_response = json.loads(redis_conn.get(TOP_COUPON))

        coupon_code_id = None
        redemptions = 0
        for key, value in sorted(redis_response.items(), key=lambda x: x[1][1], reverse=True):
            if value[0] == store.store_id:
                coupon_code_id = key
                redemptions = value[1]
                break

        if coupon_code_id is None:
            return jsonify("{}"), 404

        coupon = CouponCode.objects.filter(coupon_code_id=coupon_code_id).first().to_dict()

        coupon["redemptions"] = redemptions

        response = {
            "result": "ok",
            "coupon": coupon
        }

        return jsonify(response), 200


class NewCustomerAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def get(self):
        """
        return the total invoiced amount in the last two hours
        """

        response = results_by_store_id(request, NEW_CUSTOMERS)

        return jsonify(response), 200


class CustomerLoginAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def get(self):
        """
        return the total invoiced amount in the last two hours
        """

        response = results_by_store_id(request, CUSTOMER_LOGINS)

        return jsonify(response), 200