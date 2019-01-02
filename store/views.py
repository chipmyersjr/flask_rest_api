from flask import Blueprint


store_app = Blueprint('store_app', __name__)


@store_app.route('/store/')
def home():
    return "Hello World From Store"