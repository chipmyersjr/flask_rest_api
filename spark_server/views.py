from flask import Blueprint

from spark_server.api import TopTenCartItemsAPI, InvoiceAmountAPI

streaming_app = Blueprint('streaming_app', __name__)

top_ten_cart_view = TopTenCartItemsAPI.as_view('top_ten_cart_api')
invoice_amount_view = InvoiceAmountAPI.as_view("invoice_amount_api")

streaming_app.add_url_rule('/streaming/toptencartitems/<n>', view_func=top_ten_cart_view, methods=['GET', ])
streaming_app.add_url_rule('/streaming/invoiceamount/', view_func=invoice_amount_view, methods=['GET', ])
