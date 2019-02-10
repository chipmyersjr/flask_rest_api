from flask import Blueprint

from invoice.api import BillCartApi, InvoiceAPI

invoice_app = Blueprint('invoice_app', __name__)

bill_card_view = BillCartApi.as_view('bill_cart_api')
invoice_view = InvoiceAPI.as_view('invoice_api')

invoice_app.add_url_rule('/customer/<customer_id>/cart/billcart', view_func=bill_card_view, methods=['POST', ])
invoice_app.add_url_rule('/invoice/<invoice_id>', view_func=invoice_view, methods=['GET', ])