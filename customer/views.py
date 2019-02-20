from flask import Blueprint

from customer.api import CustomerAPI, CustomerCountAPI, CustomerAddressAPI, CustomerLogin, CustomerLogOut

customer_app = Blueprint('customer_app', __name__)

customer_view = CustomerAPI.as_view('customer_api')
customer_count_view = CustomerCountAPI.as_view('customer_count_api')
customer_address_view = CustomerAddressAPI.as_view('customer_address_api')
customer_login_view = CustomerLogin.as_view('customer_login_api')
customer_logout_view = CustomerLogOut.as_view('customer_logout_api')

customer_app.add_url_rule('/customer/', view_func=customer_view, methods=['POST', 'GET', ])
customer_app.add_url_rule('/customer/<customer_id>', view_func=customer_view, methods=['GET', 'PUT', 'DELETE', ])
customer_app.add_url_rule('/customer/count', view_func=customer_count_view, methods=['GET', ])
customer_app.add_url_rule('/customer/<customer_id>/address/', view_func=customer_address_view
                          , methods=['POST', 'GET', ])
customer_app.add_url_rule('/customer/<customer_id>/address/<address_id>/make_primary', view_func=customer_address_view
                          , methods=['PUT', ])
customer_app.add_url_rule('/customer/<customer_id>/address/<address_id>', view_func=customer_address_view
                          , methods=['DELETE', ])
customer_app.add_url_rule('/customer/login', view_func=customer_login_view, methods=['PUT', ])
customer_app.add_url_rule('/customer/logout', view_func=customer_logout_view, methods=['PUT', ])
