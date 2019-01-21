from flask import Blueprint

from cart.api import CartAPI, CartCloseAPI

cart_app = Blueprint('cart_app', __name__)

cart_view = CartAPI.as_view('cart_api')
cart_close_view = CartCloseAPI.as_view('cart_close_view')

cart_app.add_url_rule('/customer/<customer_id>/cart', view_func=cart_view, methods=['POST', 'GET', ])

cart_app.add_url_rule('/customer/<customer_id>/cart/close', view_func=cart_close_view, methods=['PUT', ])