from flask import Blueprint

from orders.api import OrderAPI, OrderShippedAPI, OrderDeliveredAPI

order_app = Blueprint('order_app', __name__)

order_view = OrderAPI.as_view('order_api')
order_shipped_view = OrderShippedAPI.as_view('order_shipped_api')
order_delivered_view = OrderDeliveredAPI.as_view('order_delivered_api')

order_app.add_url_rule('/order/<order_id>', view_func=order_view, methods=['GET', ])
order_app.add_url_rule('/order/<order_id>/shipped', view_func=order_shipped_view, methods=['PUT', ])
order_app.add_url_rule('/order/<order_id>/delivered', view_func=order_delivered_view, methods=['PUT', ])