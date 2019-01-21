from flask import Blueprint

from cart.api import CartAPI

cart_app = Blueprint('cart_app', __name__)

cart_view = CartAPI.as_view('customer_api')

cart_app.add_url_rule('/customer/<customer_id>/cart', view_func=cart_view, methods=['POST', 'GET', ])