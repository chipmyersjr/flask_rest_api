from flask import Blueprint

from product.api import ProductAPI, ProductCountAPI, ProductInventoryAPI

product_app = Blueprint('product_app', __name__)

product_view = ProductAPI.as_view('product_api')
product_count_view = ProductCountAPI.as_view('product_count_api')
product_inventory_view = ProductInventoryAPI.as_view('product_inventory_api')

product_app.add_url_rule('/product/', defaults={'product_id': None}, view_func=product_view, methods=['GET', ])
product_app.add_url_rule('/product/', view_func=product_view, methods=['POST', ])
product_app.add_url_rule('/product/<product_id>', view_func=product_view, methods=['GET', 'PUT', 'DELETE', ])

product_app.add_url_rule('/product/count', view_func=product_count_view, methods=['GET', ])

product_app.add_url_rule('/product/<product_id>/inventory', view_func=product_inventory_view, methods=['PUT', ])
