from flask import Blueprint

from spark_server.api import TopTenCartItemsAPI

streaming_app = Blueprint('streaming_app', __name__)

top_ten_cart_view = TopTenCartItemsAPI.as_view('top_ten_cart_api')

streaming_app.add_url_rule('/streaming/toptencartitems/<n>', view_func=top_ten_cart_view, methods=['GET', ])