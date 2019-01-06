from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from product.models import Product
from application import fixtures
from store.models import AccessToken


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
        fixtures(self.db_name, "store", "store/fixtures/stores")

        data = {
            "app_id": "my_dog_app",
            "app_secret": "my_dog_secret"
        }

        rv = self.app.post('/store/token/',
                           data=json.dumps(data),
                           content_type='application/json')
        token = json.loads(rv.data.decode('utf-8')).get("token")

        self.headers = {
            "APP-ID": "my_dog_app",
            "ACCESS-TOKEN": token
        }

        data = {
            "app_id": "my_furniture_app",
            "app_secret": "my_furniture_secret"
        }

        rv = self.app.post('/store/token/',
                           data=json.dumps(data),
                           content_type='application/json')
        token = json.loads(rv.data.decode('utf-8')).get("token")

        self.other_store_headers = {
            "APP-ID": "my_furniture_app",
            "ACCESS-TOKEN": token
        }

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
                           headers=self.headers,
                           content_type='application/json')
        product_id = json.loads(rv.data.decode('utf-8')).get("product")['product_id']
        assert rv.status_code == 201
        assert Product.objects.filter(product_id=product_id, deleted_at=None).count() == 1

        # test that links were created for product
        data = json.loads(rv.get_data(as_text=True))
        assert data["product"]["links"][0]["rel"] == "self"

        # test that missing field returns 400
        data = {
            "title": "Laptop",
            "product_type": "Electronics"
        }
        rv = self.app.post('/product/',
                           data=json.dumps(data),
                           headers=self.headers,
                           content_type='application/json')
        assert rv.status_code == 400
        assert "is a required property" in str(rv.data)

        # test get by product id method
        rv = self.app.get('/product/' + product_id,
                          headers=self.headers,
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
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 201
        assert json.loads(rv.data.decode('utf-8')).get('product')['title'] == "PS5"

        # test delete product
        rv = self.app.delete('/product/' + product_id,
                             headers=self.headers,
                             content_type='application/json')
        assert rv.status_code == 204
        assert Product.objects.filter(product_id=product_id, deleted_at=None).count() == 0

    def test_get_product_list(self):
        """
        Tests for the get product list endpoint
        """

        # test default get page 1
        rv = self.app.get('/product/',
                          headers=self.headers,
                          content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))
        assert rv.status_code == 200
        assert len(data["products"]) > 0
        assert data["links"][0]["href"] == "/product/?page=1"
        assert data["links"][1]["rel"] == "next"

        # test that you can get a specific page
        rv = self.app.get('/product/?page=2',
                          headers=self.headers,
                          content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))
        assert rv.status_code == 200
        assert len(data["products"]) > 0
        assert data["links"][0]["href"] == "/product/?page=2"
        assert data["links"][1]["rel"] == "previous"

        # test that not exisiting page returns 404
        rv = self.app.get('/product/?page=100',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 404

    def test_product_count(self):
        """
        Tests for the /product/count/ endpoint
        """

        # test that enpoint returns the correct count of products
        rv = self.app.get('/product/count',
                          headers=self.headers,
                          content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))

        assert rv.status_code == 200
        assert data["count"] == "19"

    def test_product_store_relationship(self):
        """
        Tests that store can only access its own products
        """
        # test get product list
        rv = self.app.get('/product/',
                          headers=self.other_store_headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert len(json.loads(rv.data.decode('utf-8')).get("products")) == 0

        # test get product list
        rv = self.app.get('/product/131077205055504776670923389866612113556',
                          headers=self.other_store_headers,
                          content_type='application/json')
        assert rv.status_code == 404

        rv = self.app.get('/product/count',
                          headers=self.headers,
                          content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))

        assert rv.status_code == 200
        assert data["count"] == "19"

    def test_method_authenications(self):
        """
        test that methods can't be be accessed without auth headers
        """
        rv = self.app.get('/product/',
                          content_type='application/json')
        assert rv.status_code == 403

        data = {
                "title": "Kitty Litter",
                "product_type": "Pets",
                "vendor": "Pet Co"
        }
        rv = self.app.put('/product/317549464512162266815167094822029596360',
                          data=json.dumps(data),
                          content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.post('/product/',
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.delete('/product/317549464512162266815167094822029596360',
                             content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.get('/product/count',
                           content_type='application/json')
        assert rv.status_code == 403