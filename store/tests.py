from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from store.models import Store


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
