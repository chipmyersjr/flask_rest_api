from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json
from datetime import datetime, timedelta

from settings import MONGODB_HOST
from store.models import Store, AccessToken


class StoreTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'stores-api-test'
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

    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)

    def test_store(self):
        """
        tests for the stores resource
        """

        # test create a store
        data = {
                    "name": "Furniture Store",
                    "tagline": "A really good furniture store",
                    "app_id": "my_furniture_app",
                    "app_secret": "my_furniture_secret"
                }
        rv = self.app.post('/store/',
                           data=json.dumps(data),
                           content_type='application/json')
        store_id = json.loads(rv.data.decode('utf-8')).get("store")['store_id']
        assert rv.status_code == 201
        assert Store.objects.filter(store_id=store_id, deleted_at=None).count() == 1

        # test that we can't create the same app_id twice
        rv = self.app.post('/store/',
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 400
        assert json.loads(rv.data.decode('utf-8')).get("error") == "APP_ID_ALREADY_EXISTS"

        # test malformed credit_order_preference
        bad_credit_data = {
            "name": "Furniture Store2",
            "tagline": "A really good furniture store",
            "app_id": "my_furniture_app2",
            "app_secret": "my_furniture_secret",
            "credit_order_preference": "Something"
        }
        rv = self.app.post('/store/',
                           data=json.dumps(bad_credit_data),
                           content_type='application/json')
        assert rv.status_code == 400

        # test get access token
        data = {
            "app_id": "my_furniture_app",
            "app_secret": "my_furniture_secret"
        }

        rv = self.app.post('/store/token/',
                           data=json.dumps(data),
                           content_type='application/json')
        token = json.loads(rv.data.decode('utf-8')).get("token")
        assert rv.status_code == 201
        assert AccessToken.objects.filter(token=token).count() == 1

        # test malformed token request
        data = {
            "app_secret": "my_furniture_secret"
        }
        rv = self.app.post('/store/token/',
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 400
        assert json.loads(rv.data.decode('utf-8')).get("error") == "'app_id' is a required property"

        # test app not found for token request
        data = {
            "app_id": "my_furniture_app3",
            "app_secret": "my_furniture_secret"
        }
        rv = self.app.post('/store/token/',
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 400
        assert json.loads(rv.data.decode('utf-8')).get("error") == "APP_ID NOT FOUND"

        # test incorrect app_secret for token request
        data = {
            "app_id": "my_furniture_app",
            "app_secret": "my_furniture_secret2"
        }
        rv = self.app.post('/store/token/',
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 400
        assert json.loads(rv.data.decode('utf-8')).get("error") == "APP_SECRET IS INCORRECT"

        # test that decorator requires app_id and token
        rv = self.app.get('/store/',
                          data=json.dumps(data),
                          content_type='application/json')
        assert rv.status_code == 403

        # test get store method
        headers = {
            "APP-ID": "my_furniture_app",
            "ACCESS-TOKEN": token
        }
        rv = self.app.get('/store/',
                          headers=headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert json.loads(rv.data.decode('utf-8')).get("store")["name"] == "Furniture Store"

        # test put method
        data = {
            "tagline": "A really great furniture store",
        }
        rv = self.app.put('/store/',
                          headers=headers,
                          data=json.dumps(data),
                          content_type='application/json')
        assert rv.status_code == 201
        assert json.loads(rv.data.decode('utf-8')).get("store")["tagline"] == "A really great furniture store"

        # test malformed credit_origin_preference
        data = {
            "credit_order_preference": "Incorrect",
        }
        rv = self.app.put('/store/',
                          headers=headers,
                          data=json.dumps(data),
                          content_type='application/json')
        assert rv.status_code == 400

        # test put method with incorrect fields
        data = {
            "incorrect_filed_name": "A really great furniture store",
        }
        rv = self.app.put('/store/',
                          headers=headers,
                          data=json.dumps(data),
                          content_type='application/json')
        assert rv.status_code == 400
        assert json.loads(rv.data.decode('utf-8')).get("error") == "No fields to update were supplied"

        # test bad token
        headers = {
            "APP-ID": "my_furniture_app",
            "ACCESS-TOKEN": 'bad-token'
        }
        rv = self.app.get('/store/',
                          headers=headers,
                          content_type='application/json')
        assert rv.status_code == 403

        # test expired token
        headers = {
            "APP-ID": "my_furniture_app",
            "ACCESS-TOKEN": token
        }
        now = datetime.now().replace(second=0, microsecond=0)
        expires = now + timedelta(days=-31)
        access = AccessToken.objects.first()
        access.expires_at = expires
        access.save()
        rv = self.app.get('/store/',
                          headers=headers,
                          content_type='application/json')
        assert rv.status_code == 403
        assert json.loads(rv.data.decode('utf-8')).get("error") == "TOKEN_EXPIRED"

        access.expires_at = datetime.now().replace(second=0, microsecond=0)
        access.save()

        # test delete method
        rv = self.app.delete('/store/',
                             headers=headers,
                             content_type='application/json')
        assert rv.status_code == 204
        assert Store.objects.filter(app_id="my_furniture_app", deleted_at=None).count() == 0


