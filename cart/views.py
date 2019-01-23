from flask import Blueprint

from cart.api import CartAPI, CartItemAPI

cart_app = Blueprint('cart_app', __name__)

cart_view = CartAPI.as_view('cart_api')
cart_item_view = CartItemAPI.as_view('cart_item_api')

cart_app.add_url_rule('/customer/<customer_id>/cart', view_func=cart_view, methods=['POST', 'GET', 'DELETE', ])
cart_app.add_url_rule('/customer/<customer_id>/cart/item/<product_id>', view_func=cart_item_view
                      , methods=["POST", "DELETE", ])
cart_app.add_url_rule('/customer/<customer_id>/cart/item', view_func=cart_item_view, methods=["POST", "DELETE"])