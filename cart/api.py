from flask.views import MethodView
from flask import request, jsonify
from datetime import datetime
import uuid


from customer.models import Customer
from store.models import Store
from store.decorators import token_required
from cart.models import Cart, ProductNotFoundException
from cart.templates import cart_obj


CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
NO_OPEN_CART = "NO_CART_IS_OPEN"


class CartAPI(MethodView):
    @token_required
    def get(self, customer_id):
        """
        returns the open cart for the customer

        Endpoint: localhost/customer/203143206815474133956265931856458093780/cart
        
        Example Response:
        {
            "cart": {
                "cart_id": "111448983167709818199901427478800268832",
                "closed_at": null,
                "created_at": "Tue, 22 Jan 2019 04:30:35 GMT",
                "invoice_created_at": null,
                "items": [
                    {
                        "added_at": "Tue, 22 Jan 2019 04:33:04 GMT",
                        "cart_item_id": "300166455149978679620982642254323085715",
                        "product_id": "58829620864631543564022316902169146987",
                        "product_title": "PS4",
                        "product_type": "Electronics",
                        "product_vendor": "Sony"
                    }
                ],
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
        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND})

        cart = Cart.objects.filter(customer_id=customer.customer_id, closed_at=None).first()
        if cart is None:
            return jsonify({"error": NO_OPEN_CART})

        response = {
            "result": "ok",
            "cart": cart_obj(cart)
        }
        return jsonify(response), 200

    @token_required
    def post(self, customer_id):
        """
        creates a cart for a customer

        Endpoint = localhost/customer/203143206815474133956265931856458093780/cart

        Example Response:
        {
            "cart": {
                "cart_id": "111448983167709818199901427478800268832",
                "closed_at": null,
                "created_at": "Tue, 22 Jan 2019 04:30:35 GMT",
                "invoice_created_at": null,
                "items": [],
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
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        cart = Cart.open_cart(customer)

        response = {
            "result": "ok",
            "cart": cart_obj(cart)
        }
        return jsonify(response), 201

    @token_required
    def delete(self, customer_id):
        """
        close a customer cart

        Endpoint localhost/customer/203143206815474133956265931856458093780/cart
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()
        customer = Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()

        if not customer:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

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


class CartItemAPI(MethodView):
    @token_required
    def post(self, customer_id=None, product_id=None):
        """
        Adds an item to the customer cart

        Endpoint: localhost/customer/203143206815474133956265931856458093780/cart/item/58829620864631543564022316902169146987

        Adds a batch of items to the customer cart

        Endpoint: localhost/customer/203143206815474133956265931856458093780/cart/item

        Example Post Body:
            [{"product_id": "12031077294672791524435788172813261083", "quantity":1}
            , {"product_id": "12031077294672791524435788172813261083", "quantity":1}]

        Example Response:
                {
            "cart": {
                "cart_id": "111448983167709818199901427478800268832",
                "closed_at": null,
                "created_at": "Tue, 22 Jan 2019 04:30:35 GMT",
                "invoice_created_at": null,
                "items": [
                    {
                        "added_at": "Tue, 22 Jan 2019 04:33:04 GMT",
                        "cart_item_id": "300166455149978679620982642254323085715",
                        "product_id": "58829620864631543564022316902169146987",
                        "product_title": "PS4",
                        "product_type": "Electronics",
                        "product_vendor": "Sony"
                    }
                ],
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
        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 400

        cart = Cart.objects.filter(customer_id=customer.customer_id, closed_at=None).first()
        if cart is None:
            cart = Cart.open_cart(customer)

        request_json = request.json

        if product_id:
            if request_json is None:
                quantity = 1
            else:
                quantity = request_json.get("quantity", 1)
            try:
                cart.add_item_to_cart(product_id, quantity)
            except ProductNotFoundException:
                return jsonify({"error": "PRODUCT_NOT_FOUND"}), 400
        else:
            cart_items_to_add = []
            for cart_item in request_json:
                try:
                    new_item = dict()
                    new_item["product_id"] = cart_item["product_id"]
                    new_item["quantity"] = cart_item["quantity"]
                    cart_items_to_add.append(new_item)
                except KeyError:
                    return jsonify({}), 400

            for item in cart_items_to_add:
                cart.add_item_to_cart(item["product_id"], item["quantity"])

        response = {
            "result": "ok",
            "cart": cart_obj(cart)
        }
        return jsonify(response), 201
