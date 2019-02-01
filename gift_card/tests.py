from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from application import fixtures
from gift_card.models import GiftCard


class GiftCardTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'customers-api-test'
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

    def test_gift_card(self):
        """
        tests for gift card resource
        """
        gifter_customer_id = "97420317489459215220140127731804389597"
        recipient_customer_id = "270069597057605288682661398313534675760"

        data = {
            "gifter_customer_id": gifter_customer_id,
            "recipient_customer_id": recipient_customer_id,
            "original_amount": 4500
        }

        # test gift card post
        rv = self.app.post('/giftcard/',
                           headers=self.headers,
                           data=json.dumps(data),
                           content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))
        gift_card_id = data["gift_card"]["gift_card_id"]
        assert rv.status_code == 201
        assert GiftCard.objects \
                       .filter(recipient_customer=recipient_customer_id, gifter_customer=gifter_customer_id) \
                       .first() \
                       .original_balance_in_cents == 4500

        rv = self.app.get('/giftcard/' + gift_card_id,
                          headers=self.headers,
                          content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))
        assert rv.status_code == 200
        assert data["gift_card"]["original_balance_in_cents"] == 4500
