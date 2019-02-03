from flask import Blueprint

from credit.api import CustomerCreditAPI

credit_app = Blueprint('credit_app', __name__)

credit_view = CustomerCreditAPI.as_view('credit_api')

credit_app.add_url_rule('/customer/<customer_id>/credit/<amount>', view_func=credit_view, methods=['POST', ])
credit_app.add_url_rule('/customer/<customer_id>/credit/<credit_id>', view_func=credit_view, methods=['DELETE', ])
