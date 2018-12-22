from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest

from settings import MONGODB_HOST


class ProductTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'products-api-test'
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

    def test_product(self):
        """test create a product"""
        data = {
                 "title": "PS4",
                 "product_type": "Electronics",
                 "vendor": "Sony"
               }

        rv = self.app.post('/product/',
                           data=data,
                           content_type='application/json')
        assert rv.status_code == 200
