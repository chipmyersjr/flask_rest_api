from flask import Flask
from flask_mongoengine import MongoEngine
from subprocess import call
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
from flask_mail import Mail
from rq import Queue
from worker import conn

from settings import MONGODB_HOST

db = MongoEngine()
mail = Mail()
redis_task_queue = Queue(connection=conn)


def create_app(**config_overrides):
    app = Flask(__name__)

    APP_ROOT = os.path.join(os.path.dirname(__file__), '..')  # refers to application_top
    dotenv_path = os.path.join(APP_ROOT, '.env')
    load_dotenv(dotenv_path)

    # Load config
    app.config.from_pyfile('settings.py')

    # apply overrides for tests
    app.config.update(config_overrides)

    # setup db
    db.init_app(app)
    mail.init_app(app)

    # set up elasticsearch
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    # import blueprints
    from product.views import product_app
    from store.views import store_app
    from customer.views import customer_app
    from cart.views import cart_app
    from gift_card.views import gift_card_app
    from credit.views import credit_app
    from invoice.views import invoice_app
    from orders.views import order_app
    from refund.views import refund_app
    from spark_server.views import streaming_app

    # register blueprints
    app.register_blueprint(product_app)
    app.register_blueprint(store_app)
    app.register_blueprint(customer_app)
    app.register_blueprint(cart_app)
    app.register_blueprint(gift_card_app)
    app.register_blueprint(credit_app)
    app.register_blueprint(invoice_app)
    app.register_blueprint(order_app)
    app.register_blueprint(refund_app)
    app.register_blueprint(streaming_app)

    return app


def fixtures(test_db, collection, fixture):
    command = "mongoimport -h %s \
        -d %s \
        -c %s \
        < %s" % (MONGODB_HOST, test_db, collection, fixture)
    call(command,  shell=True)