from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
import json

from settings import MONGODB_HOST
from application import fixtures
from invoice.models import Invoice
from invoice.models import InvoiceLineItem
from gift_card.models import GiftCard, GiftCardSpend
from credit.models import Credit
from cart.models import Cart


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
