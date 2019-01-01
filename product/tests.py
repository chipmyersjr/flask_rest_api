from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from product.models import Product


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
        """
        tests for the /product/ endpoint
        """

        # test create a product
        data = {
                 "title": "PS4",
                 "product_type": "Electronics",
                 "vendor": "Sony"
               }

        rv = self.app.post('/product/',
                           data=json.dumps(data),
                           content_type='application/json')
        product_id = json.loads(rv.data.decode('utf-8')).get("product")['product_id']
        assert rv.status_code == 201
        assert Product.objects.filter(product_id=product_id, deleted_at=None).count() == 1

        # test that missing field returns 400
        data = {
            "title": "Laptop",
            "product_type": "Electronics"
        }
        rv = self.app.post('/product/',
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 400
        assert "is a required property" in str(rv.data)

        # test get by product id method
        rv = self.app.get('/product/' + product_id,
                          content_type='application/json')
        assert rv.status_code == 200
        assert "PS4" in str(rv.data)

        # edit a product
        data = {
            "title": "PS5",
            "product_type": "Electronics",
            "vendor": "Sony"
        }
        rv = self.app.put('/pets/' + product_id,
                          data=json.dumps(data),
                          content_type='application/json')
        assert rv.status_code == 201
        assert json.loads(rv.data.decode('utf-8')).get('product')['title'] == "PS5"

        # test delete product
        rv = self.app.delete('/product/' + product_id,
                             content_type='application/json')
        assert rv.status_code == 204
        assert Product.objects.filter(product_id=product_id, deleted_at=None).count() == 0