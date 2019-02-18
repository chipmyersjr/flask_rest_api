from flask.views import MethodView
from flask import request, jsonify, abort
from datetime import datetime

from orders.models import Order, IncorrectDateFormat
from orders.templates import order_obj, order_objs
from store.models import Store
from store.decorators import token_required
from customer.models import Customer
from utils import paginated_results

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
ORDER_NOT_FOUND = "ORDER_NOT_FOUND"
INCORRECT_TIME_FORMAT = "INCORRECT_TIME_FORMAT"


class OrderAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def get(self, order_id=None):
        """

        :param order_id: order to get
        :return: order object
        """

        if order_id:
            order = Order.objects.filter(order_id=order_id).first()
            store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

            if order is None:
                return jsonify({"error": ORDER_NOT_FOUND}), 404

            if order.invoice.customer.store_id != store:
                return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

            response = {
                "result": "ok",
                "order": order_obj(order)
            }
            return jsonify(response), 200
        else:
            try:
                orders = Order.get_orders(request=request)
            except IncorrectDateFormat:
                return jsonify({"error": INCORRECT_TIME_FORMAT})

            return paginated_results(objects=orders, collection_name='order', request=request
                                     , per_page=self.PER_PAGE, serialization_func=order_objs), 200


class OrderShippedAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def put(self, order_id):
        """
        mark an order as delivered

        :param order_id: order to be updated
        :return: order
        """

        order = Order.objects.filter(order_id=order_id).first()
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        if order is None:
            return jsonify({"error": ORDER_NOT_FOUND}), 404

        if order.invoice.customer.store_id != store:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        order.status = "shipped"
        order.shipped_at = datetime.now()
        order.save()

        response = {
            "result": "ok",
            "order": order_obj(order)
        }
        return jsonify(response), 200


class OrderCanceledAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def put(self, order_id):
        """
        mark an order as canceled

        :param order_id: order to be updated
        :return: order
        """

        order = Order.objects.filter(order_id=order_id).first()
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        if order is None:
            return jsonify({"error": ORDER_NOT_FOUND}), 404

        if order.invoice.customer.store_id != store:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        order.status = "canceled"
        order.canceled_at = datetime.now()
        order.save()

        response = {
            "result": "ok",
            "order": order_obj(order)
        }
        return jsonify(response), 200


class OrderDeliveredAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def put(self, order_id):
        """
        mark an order as delivered

        :param order_id: order to be updated
        :return: order
        """

        order = Order.objects.filter(order_id=order_id).first()
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        if order is None:
            return jsonify({"error": ORDER_NOT_FOUND}), 404

        if order.invoice.customer.store_id != store:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        order.status = "delivered"
        order.delivered_at = datetime.now()
        order.save()

        response = {
            "result": "ok",
            "order": order_obj(order)
        }
        return jsonify(response), 200


class CustomerOrderAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def get(self, customer_id):
        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        try:
            orders = Order.get_orders(request=request, customer_id=customer_id)
        except IncorrectDateFormat:
            return jsonify({"error": INCORRECT_TIME_FORMAT})

        return paginated_results(objects=orders, collection_name='order', request=request
                                 , per_page=self.PER_PAGE, serialization_func=order_objs), 200