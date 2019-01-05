from flask import Blueprint

from store.api import StoreAPI, StoreTokenAPI

store_app = Blueprint('store_app', __name__)

store_view = StoreAPI.as_view('store_api')
store_token_view = StoreTokenAPI.as_view('store_token_api')

store_app.add_url_rule('/store/', view_func=store_view, methods=['POST', 'GET', 'PUT', ])
store_app.add_url_rule('/store/token/', view_func=store_token_view, methods=['POST', ])