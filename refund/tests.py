from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from application import fixtures
from refund.models import Refund
from invoice.models import Invoice
from orders.models import Order


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
        fixtures(self.db_name, "order", "orders/fixtures/orders")

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
        invoice = Invoice.objects.filter(invoice_id=invoice_id).first()
        order = Order.objects.filter(invoice=invoice).first()
        assert rv.status_code == 201
        assert len(refund.refund_line_items) == 1
        assert invoice.state == "refunded"
        assert order.status == "canceled"

        # test line item refund
        invoice_id = "5723328550124612978426097921146674393"
        data = [{
            "invoice_line_item_id": "40487189578257139583612614003166621213"
        }]
        rv = self.app.post('/invoice/' + invoice_id + "/refund",
                           headers=self.headers,
                           data=json.dumps(data),
                           content_type='application/json')
        refund = Refund.objects.filter(invoice=invoice_id).first()
        invoice = Invoice.objects.filter(invoice_id=invoice_id).first()
        assert rv.status_code == 201
        assert len(refund.refund_line_items) == 1
        assert invoice.state == "partially refunded"

        # test partial line item refund
        invoice_id = "5723328550124612978426097921146674394"
        data = [{
            "invoice_line_item_id": "40487189578257139583612614003166621214",
            "amount": 300
        }]
        rv = self.app.post('/invoice/' + invoice_id + "/refund",
                           headers=self.headers,
                           data=json.dumps(data),
                           content_type='application/json')
        refund = Refund.objects.filter(invoice=invoice_id).first()
        assert rv.status_code == 201
        assert refund.refund_line_items[0].total_amount_in_cents == 300

        # test amount refund amount
        invoice_id = "5723328550124612978426097921146674395"
        rv = self.app.post('/invoice/' + invoice_id + "/refund?amount=500",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        refund = Refund.objects.filter(invoice=invoice_id).first()
        assert rv.status_code == 201
        assert refund.refund_line_items[0].total_amount_in_cents == 500

        # test refund to credit
        invoice_id = "5723328550124612978426097921146674396"
        rv = self.app.post('/invoice/' + invoice_id + "/refund?full=true&credit=true",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        credit = Refund.objects.filter(invoice=invoice_id).first().credit
        assert rv.status_code == 201
        assert credit.original_balance_in_cents == 1000

        # test close invoice
        invoice_id = "5723328550124612978426097921146674392"
        rv = self.app.put('/invoice/' + invoice_id + "/refund/close",
                          headers=self.headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        refund = Refund.objects.filter(invoice=invoice_id).first()
        assert rv.status_code == 200
        assert refund.state == "closed"
