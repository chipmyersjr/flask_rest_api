from flask import Blueprint

from invoice.api import BillCartApi, InvoiceAPI, CustomerInvoiceAPI, InvoiceCollectedAPI

invoice_app = Blueprint('invoice_app', __name__)

bill_card_view = BillCartApi.as_view('bill_cart_api')
invoice_view = InvoiceAPI.as_view('invoice_api')
customer_invoice_view = CustomerInvoiceAPI.as_view('customer_invoice_api')
invoice_collected_view = InvoiceCollectedAPI.as_view('invoice_collected_api')

invoice_app.add_url_rule('/customer/<customer_id>/cart/billcart', view_func=bill_card_view, methods=['POST', ])
invoice_app.add_url_rule('/invoice/<invoice_id>', view_func=invoice_view, methods=['GET', ])
invoice_app.add_url_rule('/invoice/', view_func=invoice_view, methods=['GET', ])
invoice_app.add_url_rule('/customer/<customer_id>/invoices', view_func=customer_invoice_view, methods=['GET', ])
invoice_app.add_url_rule('/invoice/<invoice_id>/collected', view_func=invoice_collected_view, methods=['POST', ])
