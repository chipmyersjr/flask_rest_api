from flask.views import MethodView
from flask import request, jsonify
from datetime import datetime
import uuid


from customer.models import Customer
from store.models import Store
from store.decorators import token_required
from cart.models import Cart, CartItem
from cart.templates import cart_obj
from product.models import Product


CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
NO_OPEN_CART = "NO_CART_IS_OPEN"


class CartAPI(MethodView):
    @token_required
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
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        cart = Cart.open_cart(customer)

        response = {
            "result": "ok",
            "cart": cart_obj(cart)
        }
        return jsonify(response), 201

    @token_required
    def delete(self, customer_id):
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
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        customer = Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()
        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 400

        cart = Cart.objects.filter(customer_id=customer.customer_id, closed_at=None).first()
        if cart is None:
            cart = Cart.open_cart(customer)

        request_json = request.json
        if request_json is None:
            quantity = 1
        else:
            quantity = request_json.get("quantity", 1)

        if product_id:
            product = Product.objects.filter(product_id=product_id, store=store, deleted_at=None).first()
            if product is None:
                return jsonify({"error": "PRODUCT_NOT_FOUND"}), 400

            existing_cart_item = CartItem.objects.filter(cart_id=cart.cart_id, product_id=product.product_id
                                                         , removed_at=None).first()

            if existing_cart_item:
                existing_cart_item.quantity += quantity
                existing_cart_item.save()
            else:
                CartItem(
                    cart_item_id=str(uuid.uuid4().int),
                    product_id=product.product_id,
                    cart_id=cart.cart_id,
                    quantity=quantity
                ).save()

        response = {
            "result": "ok",
            "cart": cart_obj(cart)
        }
        return jsonify(response), 201
