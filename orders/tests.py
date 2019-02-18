from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from application import fixtures
from orders.models import Order


class OrderTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'order-api-test'
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
        fixtures(self.db_name, "gift_card", "gift_card/fixtures/gift_cards")
        fixtures(self.db_name, "credit", "credit/fixtures/credits")
        fixtures(self.db_name, "invoice", "invoice/fixtures/invoices")
        fixtures(self.db_name, "invoice_line_item", "invoice/fixtures/invoice_line_items")
        fixtures(self.db_name, "order", "orders/fixtures/orders")

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

        self.incorrect_headers = {
            "APP-ID": "my_furniture_app",
            "ACCESS-TOKEN": "INCORRECT_TOKEN"
        }

    def tearDown(self):
        db = _get_db()
        db.client.drop_database(db)

    def test_get_order(self):
        """
        test get by order id
        """
        order_id = "337552079301848591576264064507606917302"

        rv = self.app.get('/order/' + order_id,
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert json.loads(rv.get_data(as_text=True)).get('order')['order_id'] == order_id

    def test_get_order_list(self):
        """
        tests GET /order/
        """
        rv = self.app.get('/order/',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert len(json.loads(rv.get_data(as_text=True)).get("orders")) == 10

        # test status filter
        rv = self.app.get('/order/?status=shipped',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert len(json.loads(rv.get_data(as_text=True)).get("orders")) == 2

    def test_ship_order(self):
        """
        test /order/<order_id>/shipped
        """
        order_id = "10278611883944824016619297576846763820"

        rv = self.app.put('/order/' + order_id + '/shipped',
                          headers=self.headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        order = Order.objects.filter(order_id=order_id).first()
        assert rv.status_code == 200
        assert order.status == "shipped"
        assert order.shipped_at is not None

    def test_deliver_order(self):
        """
        test /order/<order_id>/shipped
        """
        order_id = "326999163998041899491828933713006160375"

        rv = self.app.put('/order/' + order_id + '/delivered',
                          headers=self.headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        order = Order.objects.filter(order_id=order_id).first()
        assert rv.status_code == 200
        assert order.status == "delivered"
        assert order.delivered_at is not None

    def test_cancel_order(self):
        """
        test /order/<order_id>/shipped
        """
        order_id = "182529164345039825253601341694848820614"

        rv = self.app.put('/order/' + order_id + '/canceled',
                          headers=self.headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        order = Order.objects.filter(order_id=order_id).first()
        assert rv.status_code == 200
        assert order.status == "canceled"
        assert order.canceled_at is not None

    def test_get_customer_orders(self):
        """
        test /customer/<customer_id>/orders
        """
        customer_id = "180422867908286360754098232165804040712"

        rv = self.app.get('/customer/' + customer_id + '/orders',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert len(json.loads(rv.get_data(as_text=True)).get("orders")) == 4

    def test_authentication(self):
        """
        tests that methods can't be accessed without authentication
        """
        order_id = "337552079301848591576264064507606917302"

        rv = self.app.get('/order/' + order_id,
                          headers=self.incorrect_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.put('/order/' + order_id + '/shipped',
                          headers=self.incorrect_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.put('/order/' + order_id + '/delivered',
                          headers=self.incorrect_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.put('/order/' + order_id + '/canceled',
                          headers=self.incorrect_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 403

        customer_id = "180422867908286360754098232165804040712"

        rv = self.app.get('/customer/' + customer_id + '/orders',
                          headers=self.incorrect_headers,
                          content_type='application/json')
        assert rv.status_code == 403

    def test_store_relationship(self):
        """
        tests that other store can't access resources
        """
        order_id = "337552079301848591576264064507606917302"

        rv = self.app.get('/order/' + order_id,
                          headers=self.other_store_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 404

        rv = self.app.put('/order/' + order_id + '/shipped',
                          headers=self.other_store_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 404

        rv = self.app.put('/order/' + order_id + '/delivered',
                          headers=self.other_store_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 404

        rv = self.app.put('/order/' + order_id + '/canceled',
                          headers=self.other_store_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 404

        rv = self.app.get('/order/',
                          headers=self.other_store_headers,
                          content_type='application/json')
        assert len(json.loads(rv.get_data(as_text=True)).get("orders")) == 0

        customer_id = "180422867908286360754098232165804040712"

        rv = self.app.get('/customer/' + customer_id + '/orders',
                          headers=self.other_store_headers,
                          content_type='application/json')
        assert len(json.loads(rv.get_data(as_text=True)).get("orders")) == 0