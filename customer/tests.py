from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json
from datetime import datetime, timedelta

from settings import MONGODB_HOST
from customer.models import Customer, Address
from application import fixtures


class CustomerTest(unittest.TestCase):
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

    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)

    def test_customer(self):
        """
        tests for the customer resource
        """

        data = {
            "currency": "USD",
            "email": "johnsmith@gmail.com",
            "first_name": "John",
            "last_name": "Smith4",
            "addresses":
                [
                    {
                        "street": "1236 Main Street",
                        "city": "townsville",
                        "zip": "1234",
                        "state": "CA",
                        "country": "USA",
                        "is_primary": "true"
                    },
                    {
                        "street": "1215 Main Street",
                        "city": "townsville",
                        "zip": "500",
                        "state": "CA",
                        "country": "USA"
                    },
                    {
                        "street": "1216 Main Street",
                        "city": "townsville",
                        "zip": "500",
                        "state": "CA",
                        "country": "USA"
                    }
                ]
        }

        rv = self.app.post('/customer/',
                           data=json.dumps(data),
                           headers=self.headers,
                           content_type='application/json')
        customer_id = json.loads(rv.data.decode('utf-8')).get("customer")['customer_id']
        assert rv.status_code == 201
        assert Customer.objects.filter(customer_id=customer_id, deleted_at=None).count() == 1
        assert Address.objects.filter(customer_id=customer_id, deleted_at=None).count() == 3

        # test that missing field returns 400
        data = {
            "currency": "USD",
            "email": "johnsmith2@gmail.com",
            "first_name": "John"
        }
        rv = self.app.post('/customer/',
                           data=json.dumps(data),
                           headers=self.headers,
                           content_type='application/json')
        assert rv.status_code == 400
        assert "is a required property" in str(rv.data)

        # test get by customer id
        rv = self.app.get('/customer/' + customer_id,
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert json.loads(rv.data.decode('utf-8')).get('customer')['email'] == "johnsmith@gmail.com"

        # edit a product
        data = {
            "currency": "EUR"
        }
        rv = self.app.put('/customer/' + customer_id,
                          data=json.dumps(data),
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 201
        assert json.loads(rv.data.decode('utf-8')).get('customer')['currency'] == "EUR"

        # test incorrect customer id return 404
        rv = self.app.put('/customer/' + str(1),
                          data=json.dumps(data),
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 404

        # test invalid fields returns 400
        data = {
            "currency_wrong": "EUR"
        }
        rv = self.app.put('/customer/' + customer_id,
                          data=json.dumps(data),
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 400
        assert json.loads(rv.data.decode('utf-8')).get('error') == "No fields supplied for update"

    def test_method_authenications(self):
        """
        test that methods can't be be accessed without auth headers
        """

        # test create a customer
        data = {
            "currency": "USD",
            "email": "johnsmith@gmail.com",
            "first_name": "John",
            "last_name": "Smith5",
            "addresses":
                [
                    {
                        "street": "1236 Main Street",
                        "city": "townsville",
                        "zip": "1234",
                        "state": "CA",
                        "country": "USA",
                        "is_primary": "true"
                    },
                    {
                        "street": "1215 Main Street",
                        "city": "townsville",
                        "zip": "500",
                        "state": "CA",
                        "country": "USA"
                    },
                    {
                        "street": "1216 Main Street",
                        "city": "townsville",
                        "zip": "500",
                        "state": "CA",
                        "country": "USA"
                    }
                ]
        }
        rv = self.app.post('/customer/',
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 403


if __name__ == '__main__':
    unittest.main()