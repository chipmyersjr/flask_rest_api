from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json
from datetime import datetime

from settings import MONGODB_HOST
from application import fixtures
from cart.models import Cart, CartItem
from customer.models import Customer
from product.models import Product


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

        customer_id = "270069597057605288682661398313534675760"


        # test customer needs to be confirmed
        rv = self.app.post('/customer/' + customer_id + '/cart',
                           headers=self.headers,
                           content_type='application/json')
        assert rv.status_code == 403
        assert json.loads(rv.get_data(as_text=True)).get('error') == "CUSTOMER_IS_NOT_CONFIRMED"

        customer = Customer.objects.filter(customer_id=customer_id).first()
        customer.confirmed_on = datetime.now()
        customer.save()

        # test working post
        customer_id = "270069597057605288682661398313534675760"

        rv = self.app.post('/customer/' + customer_id + '/cart',
                           headers=self.headers,
                           content_type='application/json')
        posted_customer = Customer.objects.filter(customer_id=customer_id).first()
        assert rv.status_code == 201
        assert Cart.objects.filter(customer_id=customer_id, closed_at=None).count() == 1
        # test last_cart_created_updated
        assert posted_customer.last_cart_created_at is not None

        # test that adding another cart closes the previous cart
        rv = self.app.post('/customer/' + customer_id + '/cart',
                           headers=self.headers,
                           content_type='application/json')
        assert rv.status_code == 201
        assert Cart.objects.filter(customer_id=customer_id, closed_at=None).count() == 1

        # test get customer cart
        rv = self.app.get('/customer/' + customer_id + '/cart',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert "items" in str(rv.data)

        # test add item to cart
        product_id = "314936113833628994682040857331370897627"
        data = {"quantity": 1}
        rv = self.app.post('/customer/' + customer_id + '/cart/item/' + product_id,
                           headers=self.headers,
                           data=json.dumps(data),
                           content_type='application/json')
        cart_id = json.loads(rv.data.decode('utf-8')).get("cart")["cart_id"]
        posted_customer = Customer.objects.filter(customer_id=customer_id).first()
        assert rv.status_code == 201
        assert CartItem.objects.filter(product_id=product_id, cart_id=cart_id, removed_at=None).count() == 1
        assert posted_customer.last_cart_activity_at is not None
        assert Product.objects.filter(product_id=product_id).first().inventory == 0

        # test can't add zero inventory item
        product_id = "314936113833628994682040857331370897627"
        data = {"quantity": 1}
        rv = self.app.post('/customer/' + customer_id + '/cart/item/' + product_id,
                           headers=self.headers,
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 404

        # test invalid customer for add cart item
        product_id = "314936113833628994682040857331370897628"
        bad_customer_id = "123"
        rv = self.app.post('/customer/' + bad_customer_id + '/cart/item/' + product_id,
                           headers=self.headers,
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 404

        # add cart item...test default quantity is 1
        product_id = "314936113833628994682040857331370897629"
        rv = self.app.post('/customer/' + customer_id + '/cart/item/' + product_id,
                           headers=self.headers,
                           data=json.dumps({}),
                           content_type='application/json')
        cart_id = json.loads(rv.data.decode('utf-8')).get("cart")["cart_id"]
        assert rv.status_code == 201
        assert CartItem.objects.filter(product_id=product_id, cart_id=cart_id, removed_at=None).first().quantity == 1

        # add cart item...test bad product id returns 400
        bad_product_id = "123"
        rv = self.app.post('/customer/' + customer_id + '/cart/item/' + bad_product_id,
                           headers=self.headers,
                           data=data,
                           content_type='application/json')
        assert rv.status_code == 400

        # add cart item....test that adding existing product add to quantity
        product_id = "314936113833628994682040857331370897627"
        data = {
            "amount": 5
        }
        rv = self.app.put('/product/' + product_id + '/inventory',
                          data=json.dumps(data),
                          headers=self.headers,
                          content_type='application/json')
        data = {"quantity": 2}
        rv = self.app.post('/customer/' + customer_id + '/cart/item/' + product_id,
                           headers=self.headers,
                           data=json.dumps(data),
                           content_type='application/json')
        cart_id = json.loads(rv.data.decode('utf-8')).get("cart")["cart_id"]
        assert rv.status_code == 201
        assert CartItem.objects.filter(product_id=product_id, cart_id=cart_id, removed_at=None).count() == 1
        assert CartItem.objects.filter(product_id=product_id, cart_id=cart_id, removed_at=None).first().quantity == 3

        # test update product quantity
        data = {"quantity": 2}
        rv = self.app.put('/customer/' + customer_id + '/cart/item/' + product_id,
                          headers=self.headers,
                          data=json.dumps(data),
                          content_type='application/json')
        cart_id = json.loads(rv.data.decode('utf-8')).get("cart")["cart_id"]
        assert rv.status_code == 200
        assert CartItem.objects.filter(product_id=product_id, cart_id=cart_id, removed_at=None).first().quantity == 2

        # test add multiple products
        batch_data = [{"product_id": "314936113833628994682040857331370897630", "quantity": 1},
                      {"product_id": "314936113833628994682040857331370897631", "quantity": 1}]
        rv = self.app.post('/customer/' + customer_id + '/cart/item',
                           headers=self.headers,
                           data=json.dumps(batch_data),
                           content_type='application/json')
        cart_id = json.loads(rv.data.decode('utf-8')).get("cart")["cart_id"]
        assert rv.status_code == 201
        assert CartItem.objects.filter(cart_id=cart_id, removed_at=None).count() == 4

        # test add multiple products - malformed request
        batch_data = [{"product_id": "314936113833628994682040857331370897630", "quantity": 1},
                      {"product_id": "314936113833628994682040857331370897631"}]
        rv = self.app.post('/customer/' + customer_id + '/cart/item',
                           headers=self.headers,
                           data=json.dumps(batch_data),
                           content_type='application/json')
        assert rv.status_code == 400

        # test delete product
        product_id = "314936113833628994682040857331370897630"
        rv = self.app.delete('/customer/' + customer_id + '/cart/item/' + product_id,
                             headers=self.headers,
                             content_type='application/json')
        assert rv.status_code == 200
        assert CartItem.objects.filter(cart_id=cart_id, removed_at=None, product_id=product_id).count() == 0

        # test delete batch product
        delete_date = [{"product_id": "314936113833628994682040857331370897627"},
                       {"product_id": "314936113833628994682040857331370897631"}]
        rv = self.app.delete('/customer/' + customer_id + '/cart/item',
                             headers=self.headers,
                             data=json.dumps(delete_date),
                             content_type='application/json')
        assert rv.status_code == 200
        assert CartItem.objects.filter(cart_id=cart_id, removed_at=None).count() == 1
        assert Product.objects.filter(product_id=product_id).first().inventory == 10

        # test close cart
        rv = self.app.delete('/customer/' + customer_id + '/cart',
                             headers=self.headers,
                             content_type='application/json')
        assert rv.status_code == 200
        assert Cart.objects.filter(customer_id=customer_id, closed_at=None).count() == 0

        # test close cart with no open cart return 404
        rv = self.app.delete('/customer/' + customer_id + '/cart',
                             headers=self.headers,
                             content_type='application/json')
        assert rv.status_code == 404

        # test add item to cart with no cart will create new cart
        product_id = "314936113833628994682040857331370897628"
        rv = self.app.post('/customer/' + customer_id + '/cart/item/' + product_id,
                           headers=self.headers,
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 201
        assert Cart.objects.filter(customer_id=customer_id, closed_at=None).count() == 1

    def test_cart_authentication(self):
        """
        test that methods can't be reached without auth
        """
        incorrect_headers = {
            "APP-ID": "my_furniture_app",
            "ACCESS-TOKEN": "INCORRECT_TOKEN"
        }

        customer_id = "180422867908286360754098232165804040712"

        # confirm customer so cart usage is allowed
        customer = Customer.objects.filter(customer_id=customer_id).first()
        customer.confirmed_on = datetime.now()
        customer.save()

        rv = self.app.post('/customer/' + customer_id + '/cart',
                           headers=incorrect_headers,
                           content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.post('/customer/' + customer_id + '/cart',
                           content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.get('/customer/' + customer_id + '/cart',
                          headers=incorrect_headers,
                          content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.get('/customer/' + customer_id + '/cart',
                          content_type='application/json')
        assert rv.status_code == 403

        product_id = "314936113833628994682040857331370897627"
        data = {"quantity": 1}
        rv = self.app.post('/customer/' + customer_id + '/cart/item/' + product_id,
                           headers=incorrect_headers,
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.post('/customer/' + customer_id + '/cart/item/' + product_id,
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.delete('/customer/' + customer_id + '/cart',
                             headers=incorrect_headers,
                             content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.delete('/customer/' + customer_id + '/cart',
                             content_type='application/json')
        assert rv.status_code == 403

        product_id = "6451551371292750404649077474474125035"
        rv = self.app.delete('/customer/' + customer_id + '/cart/item/' + product_id,
                             headers=incorrect_headers,
                             content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.delete('/customer/' + customer_id + '/cart/item/' + product_id,
                             content_type='application/json')
        assert rv.status_code == 403

    def test_cart_store_relationship(self):
        """
        test that store can only access its own carts
        """
        # test get cart
        customer_id = "180422867908286360754098232165804040712"

        # confirm customer so cart usage is allowed
        customer = Customer.objects.filter(customer_id=customer_id).first()
        customer.confirmed_on = datetime.now()
        customer.save()

        rv = self.app.get('/customer/' + customer_id + '/cart',
                          headers=self.other_store_headers,
                          content_type='application/json')
        assert rv.status_code == 404

        # test add item to cart
        product_id = "314936113833628994682040857331370897627"
        data = {"quantity": 1}
        rv = self.app.post('/customer/' + customer_id + '/cart/item/' + product_id,
                           headers=self.other_store_headers,
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 404

        # test delete product
        product_id = "314936113833628994682040857331370897630"
        rv = self.app.delete('/customer/' + customer_id + '/cart/item/' + product_id,
                             headers=self.other_store_headers,
                             content_type='application/json')
        assert rv.status_code == 404

        # test close cart
        rv = self.app.delete('/customer/' + customer_id + '/cart',
                             headers=self.other_store_headers,
                             content_type='application/json')
        assert rv.status_code == 404
