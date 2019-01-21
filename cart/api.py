from flask.views import MethodView
from flask import request, jsonify
from datetime import datetime
import uuid


from customer.models import Customer
from store.models import Store
from cart.models import Cart
from cart.templates import cart_obj


class CartAPI(MethodView):
    def post(self, customer_id):
        """
        creates a cart for a customer

        Endpoint = localhost/customer/203143206815474133956265931856458093780/cart

        Example Response:
        {
            "cart": {
                "cart_id": "26085018984094060322407184395495101838",
                "closed_at": null,
                "created_at": "Mon, 21 Jan 2019 20:16:53 GMT",
                "invoice_created_at": null,
                "last_item_added_at": null,
                "links": [
                    {
                        "href": "/customer/203143206815474133956265931856458093780/cart",
                        "rel": "self"
                    },
                    {
                        "href": "/customer/203143206815474133956265931856458093780",
                        "rel": "customer"
                    }
                ],
                "state": "open"
            },
            "result": "ok"
        }
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        customer = Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()
        if not customer:
            return jsonify({"error": "CUSTOMER_NOT_FOUND"}), 404

        existing_cart = Cart.objects.filter(customer_id=customer_id, closed_at=None).first()

        if existing_cart:
            existing_cart.closed_at = datetime.now()
            existing_cart.state = "closed"
            existing_cart.save()

        cart = Cart(
            cart_id=str(uuid.uuid4().int),
            customer_id=customer.customer_id
        ).save()

        response = {
            "result": "ok",
            "cart": cart_obj(cart)
        }
        return jsonify(response), 201

    def delete(self, customer_id):
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()
        customer = Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()

        if not customer:
            return jsonify({"error": "CUSTOMER_NOT_FOUND"}), 404

        cart = Cart.objects.filter(customer_id=customer_id, closed_at=None).first()

        if not cart:
            return jsonify({}), 404

        cart.closed_at = datetime.now()
        cart.state = 'closed'
        cart.save()

        response = {
            "result": "ok",
            "cart": cart_obj(cart)
        }
        return jsonify(response), 200
