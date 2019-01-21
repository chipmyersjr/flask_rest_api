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
            "customer": cart_obj(cart)
        }
        return jsonify(response), 201
