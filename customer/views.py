from flask import Blueprint

from customer.api import CustomerAPI, CustomerCountAPI

customer_app = Blueprint('customer_app', __name__)

customer_view = CustomerAPI.as_view('customer_api')
customer_count_view = CustomerCountAPI.as_view('customer_count_api')

customer_app.add_url_rule('/customer/', view_func=customer_view, methods=['POST', 'GET', ])
customer_app.add_url_rule('/customer/<customer_id>', view_func=customer_view, methods=['GET', 'PUT', 'DELETE', ])

customer_app.add_url_rule('/customer/count', view_func=customer_count_view, methods=['GET', ])