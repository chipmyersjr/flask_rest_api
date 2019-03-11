from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from application import fixtures
from refund.models import Refund


class RefundTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'invoice-api-test'
        return create_app_base(
            MONGODB_SETTINGS={'DB': self.db_name,
                              'HOST': MONGODB_HOST},
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY='mySecret!',
        )

    def setUp(self):
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()
        fixtures(self.db_name, "store", "store/fixtures/stores")
        fixtures(self.db_name, "customer", "customer/fixtures/customers")
        fixtures(self.db_name, "product", "product/fixtures/products.json")
        fixtures(self.db_name, "cart", "cart/fixtures/cart")
        fixtures(self.db_name, "cart_item", "cart/fixtures/cart_items")
        fixtures(self.db_name, "gift_card", "gift_card/fixtures/gift_cards")
        fixtures(self.db_name, "credit", "credit/fixtures/credits")
        fixtures(self.db_name, "invoice", "invoice/fixtures/invoices")
        fixtures(self.db_name, "invoice_line_item", "invoice/fixtures/invoice_line_items")

        data = {
            "app_id": "my_furniture_app",
            "app_secret": "my_furniture_secret"
        }

        rv = self.app.post('/store/token/',
                           data=json.dumps(data),
                           content_type='application/json')
        token = json.loads(rv.data.decode('utf-8')).get("token")

        self.headers = {
            "APP-ID": "my_furniture_app",
            "ACCESS-TOKEN": token
        }

        data = {
            "app_id": "my_dog_app",
            "app_secret": "my_dog_secret"
        }

        rv = self.app.post('/store/token/',
                           data=json.dumps(data),
                           content_type='application/json')
        token = json.loads(rv.data.decode('utf-8')).get("token")

        self.other_store_headers = {
            "APP-ID": "my_dog_app",
            "ACCESS-TOKEN": token
        }

        self.incorrect_headers = {
            "APP-ID": "my_furniture_app",
            "ACCESS-TOKEN": "INCORRECT_TOKEN"
        }

    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)

    def test_refund(self):
        invoice_id = "5723328550124612978426097921146674392"

        rv = self.app.post('/invoice/' + invoice_id + "/refund?full=true",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        refund = Refund.objects.filter(invoice=invoice_id).first()
        assert rv.status_code == 201
        assert len(refund.refund_line_items) == 1