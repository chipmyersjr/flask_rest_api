from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from product.models import Product
from application import fixtures


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
        fixtures(self.db_name, "product", "product/fixtures/products.json")

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
        rv = self.app.put('/product/' + product_id,
                          data=json.dumps(data),
                          content_type='application/json')
        assert rv.status_code == 201
        assert json.loads(rv.data.decode('utf-8')).get('product')['title'] == "PS5"

        # test delete product
        rv = self.app.delete('/product/' + product_id,
                             content_type='application/json')
        assert rv.status_code == 204
        assert Product.objects.filter(product_id=product_id, deleted_at=None).count() == 0

    def test_get_product_list(self):
        """
        Tests for the get product list endpoint
        """

        # test default get page 1
        rv = self.app.get('/product/',
                          content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))
        assert rv.status_code == 200
        assert len(data["products"]) > 0
        assert data["links"][0]["href"] == "/product/?page=1"
        assert data["links"][1]["rel"] == "next"

        # test that you can get a specific page
        rv = self.app.get('/product/?page=2',
                          content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))
        assert rv.status_code == 200
        assert len(data["products"]) > 0
        assert data["links"][0]["href"] == "/product/?page=2"
        assert data["links"][1]["rel"] == "previous"

    def test_product_count(self):
        """
        Tests for the /product/count/ endpoint
        """

        # test that enpoint returns the correct count of products
        rv = self.app.get('/product/count',
                          content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))

        assert rv.status_code == 200
        assert data["count"] == "19"
