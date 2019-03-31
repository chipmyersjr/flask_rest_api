from flask import Blueprint

from invoice.api import BillCartApi, InvoiceAPI, CustomerInvoiceAPI, InvoiceCollectedAPI, InvoiceFailedAPI
from invoice.api import CouponCodeAPI

invoice_app = Blueprint('invoice_app', __name__)

bill_card_view = BillCartApi.as_view('bill_cart_api')
invoice_view = InvoiceAPI.as_view('invoice_api')
customer_invoice_view = CustomerInvoiceAPI.as_view('customer_invoice_api')
invoice_collected_view = InvoiceCollectedAPI.as_view('invoice_collected_api')
invoice_failed_view = InvoiceFailedAPI.as_view('invoice_failed_api')
coupon_code_view = CouponCodeAPI.as_view('coupon_api')

invoice_app.add_url_rule('/customer/<customer_id>/cart/billcart', view_func=bill_card_view, methods=['POST', ])
invoice_app.add_url_rule('/invoice/<invoice_id>', view_func=invoice_view, methods=['GET', ])
invoice_app.add_url_rule('/invoice/', view_func=invoice_view, methods=['GET', ])
invoice_app.add_url_rule('/customer/<customer_id>/invoices', view_func=customer_invoice_view, methods=['GET', ])
invoice_app.add_url_rule('/invoice/<invoice_id>/collected', view_func=invoice_collected_view, methods=['POST', ])
invoice_app.add_url_rule('/invoice/<invoice_id>/failed', view_func=invoice_failed_view, methods=['PUT', ])

invoice_app.add_url_rule('/coupon_code/', view_func=coupon_code_view, methods=['POST', ])