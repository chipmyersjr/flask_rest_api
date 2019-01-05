from flask import Blueprint

from store.api import StoreAPI

store_app = Blueprint('store_app', __name__)

store_view = StoreAPI.as_view('product_api')

store_app.add_url_rule('/store/', view_func=store_view, methods=['POST', ])
