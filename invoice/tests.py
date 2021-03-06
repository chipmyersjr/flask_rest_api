from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json
from datetime import datetime
from time import sleep

from settings import MONGODB_HOST
from application import fixtures
from invoice.models import Invoice, CouponCode, CouponCodeRedemption
from invoice.models import InvoiceLineItem
from gift_card.models import GiftCard, GiftCardSpend
from credit.models import Credit, CreditRedemption
from cart.models import Cart
from orders.models import Order, OrderLineItem
from customer.models import Customer


class InvoiceTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'invoice-api-test'
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

    def test_bill_cart(self):
        """
        test that carts a billed correctly
        """

        """
        test that:
        invoice record is created
        line item records are created 
        total in cents and sub total in cents are calculated
        gift card is applied
        credit is applied
        test cart is closed
        gift card spend records are created
        """
        customer_id = "180422867908286360754098232165804040712"
        gift_card_id = "130774321679366772547251016213112148452"
        credit_id = "201285773978942914054186556756783888772"
        cart_id = "111448983167709818199901427478800268832"

        rv = self.app.post('/customer/' + customer_id + "/cart/billcart",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        invoice_id = json.loads(rv.get_data(as_text=True)).get('invoice')['invoice_id']
        assert Invoice.objects.filter(invoice_id=invoice_id).count() == 1
        assert InvoiceLineItem.objects.filter(invoice=invoice_id).count() == 3
        assert json.loads(rv.get_data(as_text=True)).get('invoice')['total_amount_in_cents'] == 5000
        assert json.loads(rv.get_data(as_text=True)).get('invoice')['subtotal_amount_in_cents'] == 3500
        assert Invoice.objects.filter(invoice_id=invoice_id).first().gift_card_used_amount_in_cents == 500
        assert GiftCard.objects.filter(gift_card_id=gift_card_id).first().current_balance_in_cents == 0
        assert Credit.objects.filter(credit_id=credit_id).first().current_balance_in_cents == 0
        assert Cart.objects.filter(cart_id=cart_id).first().state == 'billed'
        assert Cart.objects.filter(cart_id=cart_id).first().invoice_created_at is not None
        assert GiftCardSpend.objects.filter(gift_card=gift_card_id).first().amount == 500
        assert GiftCardSpend.objects.filter(gift_card=gift_card_id).first().remaining_balance == 0
        assert CreditRedemption.objects.filter(credit=credit_id).first().amount == 1000
        assert CreditRedemption.objects.filter(credit=credit_id).first().remaining_balance == 0

        # test that the cart can't be billed again
        rv = self.app.post('/customer/' + customer_id + "/cart/billcart",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert rv.status_code == 404

        # test get invoice method
        rv = self.app.get('/invoice/' + invoice_id,
                          headers=self.headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 200
        assert json.loads(rv.get_data(as_text=True)).get('invoice')['subtotal_amount_in_cents'] == 3500

        # test a customer with multiple credits and giftcards
        customer_id = "264356367106300022542696282926073711663"
        rv = self.app.post('/customer/' + customer_id + "/cart/billcart",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        invoice_id = json.loads(rv.get_data(as_text=True)).get('invoice')['invoice_id']
        assert Invoice.objects.filter(invoice_id=invoice_id).count() == 1
        assert InvoiceLineItem.objects.filter(invoice=invoice_id).count() == 6
        assert json.loads(rv.get_data(as_text=True)).get('invoice')['total_amount_in_cents'] == 6000
        assert json.loads(rv.get_data(as_text=True)).get('invoice')['subtotal_amount_in_cents'] == 3000

        # test customer with a remaining gift card balance
        customer_id = "296529713197755837865132719265086141839"
        gift_card_id = "130774321679366772547251016213112148456"

        rv = self.app.post('/customer/' + customer_id + "/cart/billcart",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert json.loads(rv.get_data(as_text=True)).get('invoice')['total_amount_in_cents'] == 1000
        assert json.loads(rv.get_data(as_text=True)).get('invoice')['subtotal_amount_in_cents'] == 0
        assert GiftCard.objects.filter(gift_card_id=gift_card_id).first().current_balance_in_cents == 1000

        # test customer with a remaining credit balance
        customer_id = "149491126147831591325310335857431011103"
        credit_id = "201285773978942914054186556756783888776"

        rv = self.app.post('/customer/' + customer_id + "/cart/billcart",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert json.loads(rv.get_data(as_text=True)).get('invoice')['total_amount_in_cents'] == 1000
        assert json.loads(rv.get_data(as_text=True)).get('invoice')['subtotal_amount_in_cents'] == 0
        assert Credit.objects.filter(credit_id=credit_id).first().current_balance_in_cents == 1000

    def test_get_invoice_list(self):
        """
        test the GET /invoice/ method
        """
        rv = self.app.get('/invoice/',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert len(json.loads(rv.get_data(as_text=True)).get('invoices')) == 4

        # test closed query parameter
        rv = self.app.get('/invoice/?closed=true',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert len(json.loads(rv.get_data(as_text=True)).get('invoices')) == 10

        # test customer invoice list
        customer_id = "180422867908286360754098232165804040712"
        rv = self.app.get('/customer/' + customer_id + '/invoices',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert len(json.loads(rv.get_data(as_text=True)).get('invoices')) == 3

    def test_collected_invoice(self):
        """
        test that invoices can be marked as collected and that orders are created
        """
        invoice_id = "5723328550124612978426097921146674391"
        customer_id = "207041015150729681304475393352873932232"

        rv = self.app.post('/invoice/' + invoice_id + '/collected',
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        order = Order.objects.filter(invoice=invoice_id).first()
        customer = Customer.objects.filter(customer_id=customer_id).first()
        assert rv.status_code == 201
        assert Invoice.objects.filter(invoice_id=invoice_id).first().state == "collected"
        assert order.status == "pending"
        assert OrderLineItem.objects.filter(order=order).first().quantity == 1
        assert customer.last_order_date is not None
        assert customer.total_spent == 1000

    def test_failed_invoice(self):
        """
        test that invoice can be failed properly
        """
        invoice_id = "5723328550124612978426097921146674389"

        rv = self.app.put('/invoice/' + invoice_id + '/failed',
                          headers=self.headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 200
        assert Invoice.objects.filter(invoice_id=invoice_id).first().state == "failed"
        assert Invoice.objects.filter(invoice_id=invoice_id).first().state == "failed"

    def test_authentication(self):
        """
        tests that methods can't be accessed without authentication
        """
        customer_id = "207041015150729681304475393352873932232"
        rv = self.app.post('/customer/' + customer_id + "/cart/billcart",
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.post('/customer/' + customer_id + "/cart/billcart",
                           data=json.dumps("{}"),
                           headers=self.incorrect_headers,
                           content_type='application/json')
        assert rv.status_code == 403

        invoice_id = "5723328550124612978426097921146674387"
        rv = self.app.get('/invoice/' + invoice_id,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.get('/invoice/' + invoice_id,
                          data=json.dumps("{}"),
                          headers=self.incorrect_headers,
                          content_type='application/json')
        assert rv.status_code == 403

        customer_id = "180422867908286360754098232165804040712"
        rv = self.app.get('/customer/' + customer_id + '/invoices',
                          content_type='application/json')
        assert rv.status_code == 403

        rv = self.app.get('/customer/' + customer_id + '/invoices',
                          headers=self.incorrect_headers,
                          content_type='application/json')
        assert rv.status_code == 403

        invoice_id = "5723328550124612978426097921146674391"

        rv = self.app.post('/invoice/' + invoice_id + '/collected',
                           headers=self.incorrect_headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert rv.status_code == 403

        invoice_id = "5723328550124612978426097921146674387"

        rv = self.app.put('/invoice/' + invoice_id + '/failed',
                          headers=self.incorrect_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 403

    def test_store_relationship(self):
        """
        tests that other store can't access resources
        """
        customer_id = "207041015150729681304475393352873932232"
        rv = self.app.post('/customer/' + customer_id + "/cart/billcart",
                           headers=self.other_store_headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert rv.status_code == 404

        invoice_id = "5723328550124612978426097921146674387"
        rv = self.app.get('/invoice/' + invoice_id,
                          headers=self.other_store_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 404

        customer_id = "180422867908286360754098232165804040712"
        rv = self.app.get('/customer/' + customer_id + '/invoices',
                          headers=self.other_store_headers,
                          content_type='application/json')
        assert rv.status_code == 404

        invoice_id = "5723328550124612978426097921146674389"
        rv = self.app.post('/invoice/' + invoice_id + '/collected',
                           headers=self.other_store_headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert rv.status_code == 404

        invoice_id = "5723328550124612978426097921146674387"

        rv = self.app.put('/invoice/' + invoice_id + '/failed',
                          headers=self.other_store_headers,
                          data=json.dumps("{}"),
                          content_type='application/json')
        assert rv.status_code == 404

    def test_coupon_code(self):
        """
        tests the coupon code resource
        """

        # create coupon code
        rv = self.app.post('/coupon_code/?code=test&expires_at=2050031508&style=dollars_off&amount=500',
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        coupon = CouponCode.objects.filter(code="test").first()
        assert rv.status_code == 201
        assert coupon.code == "test"
        assert coupon.expires_at is not None
        assert coupon.style == "dollars_off"
        assert coupon.amount == 500

        # test redemption
        customer_id = "165886225230149151116807354302376343571"

        rv = self.app.post('/customer/' + customer_id + "/cart/billcart?coupon=test",
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        redemption = CouponCodeRedemption.objects.filter(coupon_code=coupon).first()
        assert rv.status_code == 201
        assert redemption.amount_in_cents == 500
        assert redemption.coupon_code.code == "test"
        assert redemption.invoice.get_subtotal_amount() == 500

        # test duplicate coupon code returns 400
        rv = self.app.post('/coupon_code/?code=test&expires_at=2019031508&style=percent_off&amount=5',
                           headers=self.headers,
                           data=json.dumps("{}"),
                           content_type='application/json')
        assert rv.status_code == 400
        assert CouponCode.objects.filter(code="test").count() == 1

        # test check is valid returns true
        rv = self.app.get('/coupon_code/test/is_valid',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert json.loads(rv.get_data(as_text=True)).get("result") == True

        # expired coupon coid returns false
        coupon.expires_at = datetime.now()
        coupon.save()
        sleep(2)

        rv = self.app.get('/coupon_code/test/is_valid',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert json.loads(rv.get_data(as_text=True)).get("result") == False

        # test void coupon code
        self.app.post('/coupon_code/?code=test2&expires_at=2050031508&style=percent_off&amount=5',
                      headers=self.headers,
                      data=json.dumps("{}"),
                      content_type='application/json')

        rv = self.app.delete('/coupon_code/test2',
                             headers=self.headers,
                             content_type='application/json')
        coupon = CouponCode.objects.filter(code="test2").first()
        assert rv.status_code == 204
        assert coupon.voided_at is not None

        # void coupon code returns false
        rv = self.app.get('/coupon_code/test2/is_valid',
                          headers=self.headers,
                          content_type='application/json')
        assert rv.status_code == 200
        assert json.loads(rv.get_data(as_text=True)).get("result") == False