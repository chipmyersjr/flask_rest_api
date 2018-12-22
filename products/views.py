from flask import Blueprint

product_app = Blueprint('product_app', __name__)


@product_app.route('/')
def home():
    return "Here are some products"