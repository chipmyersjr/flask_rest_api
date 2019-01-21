from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from application import fixtures
from cart.models import Cart


class CartTest(unittest.TestCase):
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

    def test_cart(self):
        """
        tests for cart resourse
        """
        # test posting for non-existant customer returns 404
        customer_id = "123"

        rv = self.app.post('/customer/' + customer_id + '/cart',
                           headers=self.headers,
                           content_type='application/json')
        assert rv.status_code == 404
        assert json.loads(rv.data.decode('utf-8')).get('error') == "CUSTOMER_NOT_FOUND"

        # test working post
        customer_id = "270069597057605288682661398313534675760"

        rv = self.app.post('/customer/' + customer_id + '/cart',
                           headers=self.headers,
                           content_type='application/json')
        assert rv.status_code == 201
        assert Cart.objects.filter(customer_id=customer_id, closed_at=None).count() == 1

        # test that adding another cart closes the previous cart
        rv = self.app.post('/customer/' + customer_id + '/cart',
                           headers=self.headers,
                           content_type='application/json')
        assert rv.status_code == 201
        assert Cart.objects.filter(customer_id=customer_id, closed_at=None).count() == 1

        # test close cart
        rv = self.app.put('/customer/' + customer_id + '/cart/close',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert Cart.objects.filter(customer_id=customer_id, closed_at=None).count() == 0

        # test close cart with no open cart return 404
        rv = self.app.put('/customer/' + customer_id + '/cart/close',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 404