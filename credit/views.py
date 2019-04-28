from flask import Blueprint

from credit.api import CustomerCreditAPI, CustomerBatchCreditAPI

credit_app = Blueprint('credit_app', __name__)

credit_view = CustomerCreditAPI.as_view('credit_api')
credit_batch_view = CustomerBatchCreditAPI.as_view('credit_batch_api')

credit_app.add_url_rule('/customer/<customer_id>/credit/<amount>', view_func=credit_view, methods=['POST', ])
credit_app.add_url_rule('/customer/<customer_id>/credit/<credit_id>', view_func=credit_view, methods=['DELETE', ])
credit_app.add_url_rule('/customer/<customer_id>/credit', view_func=credit_view, methods=['GET', ])

credit_app.add_url_rule('/customer/credit/<amount>', view_func=credit_batch_view, methods=['POST', ])
credit_app.add_url_rule('/customer/credit/status/<job_id>', view_func=credit_batch_view, methods=['GET', ])