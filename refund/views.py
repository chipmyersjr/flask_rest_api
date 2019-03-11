from flask import Blueprint

from refund.api import RefundAPI

refund_app = Blueprint('refund_app', __name__)

refund_view = RefundAPI.as_view('refund_api')

refund_app.add_url_rule('/invoice/<invoice_id>/refund', view_func=refund_view, methods=['POST', ])