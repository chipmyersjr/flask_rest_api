from flask import Blueprint

from product.api import ProductAPI, ProductCountAPI, ProductInventoryAPI, ProductTagAPI, ProductSearchAPI

product_app = Blueprint('product_app', __name__)

product_view = ProductAPI.as_view('product_api')
product_count_view = ProductCountAPI.as_view('product_count_api')
product_inventory_view = ProductInventoryAPI.as_view('product_inventory_api')
product_tag_view = ProductTagAPI.as_view('product_tag_api')
product_search_api = ProductSearchAPI.as_view('product_search_api')

product_app.add_url_rule('/product/', defaults={'product_id': None}, view_func=product_view, methods=['GET', ])
product_app.add_url_rule('/product/', view_func=product_view, methods=['POST', ])
product_app.add_url_rule('/product/<product_id>', view_func=product_view, methods=['GET', 'PUT', 'DELETE', ])

product_app.add_url_rule('/product/count', view_func=product_count_view, methods=['GET', ])

product_app.add_url_rule('/product/<product_id>/inventory', view_func=product_inventory_view, methods=['PUT', ])
product_app.add_url_rule('/product/<product_id>/tag/<tag>', view_func=product_tag_view, methods=['POST', ])
product_app.add_url_rule('/product/<product_id>/tag/', view_func=product_tag_view, methods=['DELETE', ])

product_app.add_url_rule('/product/search/<query>', view_func=product_search_api, methods=['GET', ])