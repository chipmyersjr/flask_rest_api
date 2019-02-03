from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from application import fixtures
from credit.models import Credit
from customer.models import Customer


class CreditTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'credit-api-test'
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

    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)

    def test_credit(self):
        """
        tests for the credit resource
        """
        customer_id = "7703254127253629093471751051825874859"

        # test issue credit to customer
        rv = self.app.post('/customer/' + customer_id + "/credit/1000",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert rv.status_code == 201
        assert Credit.objects.filter(customer=customer_id).first().original_balance_in_cents == 1000

        # test error message for non-int amount
        rv = self.app.post('/customer/' + customer_id + "/credit/cat",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert rv.status_code == 400
        assert json.loads(rv.get_data(as_text=True)).get("error") == "AMOUNT_SHOULD_BE_INT"
