from application import db
from datetime import datetime
import uuid

from product.models import Product
from customer.models import Customer


class ProductNotFoundException(Exception):
    """
    Exception when product is not found
    """
    pass


class Cart(db.Document):
    cart_id = db.StringField(db_field="cart_id", primary_key=True)
    customer_id = db.ReferenceField(Customer, db_field="customer_id")
    state = db.StringField(default="open")
    created_at = db.DateTimeField(default=datetime.now())
    last_item_added_at = db.DateTimeField()
    invoice_created_at = db.DateTimeField()
    closed_at = db.DateTimeField()

    meta = {
        'indexes': [('customer_id', 'closed_at')]
    }

    @classmethod
    def open_cart(cls, customer):
        """
        opens a cart for given customer

        :param customer: customer document object
        :return: newly created cart object
        """
        existing_cart = Cart.objects.filter(customer_id=customer.customer_id, closed_at=None).first()

        if existing_cart:
            existing_cart.closed_at = datetime.now()
            existing_cart.state = "closed"
            existing_cart.save()

        cart = Cart(
            cart_id=str(uuid.uuid4().int),
            customer_id=customer.customer_id
        ).save()

        customer.last_cart_created_at = datetime.now()
        customer.updated_at = datetime.now()
        customer.save()

        return cart

    def add_item_to_cart(self, product_id, quantity):
        """
        Add an item to customers current cart

        :param product_id: product id string
        :param quantity: amount of items added
        :return: newly created or existing cart item
        """
        product = Product.objects.filter(product_id=product_id, store=self.customer_id.store_id, deleted_at=None).first()
        if product is None:
            raise ProductNotFoundException

        existing_cart_item = CartItem.objects.filter(cart_id=self.cart_id, product_id=product.product_id
                                                     , removed_at=None).first()

        self.customer_id.last_cart_activity_at = datetime.now()
        self.customer_id.updated_at = datetime.now()
        self.customer_id.save()
        if existing_cart_item:
            existing_cart_item.quantity += quantity
            existing_cart_item.save()
            return existing_cart_item
        else:
            cart_item = CartItem(
                cart_item_id=str(uuid.uuid4().int),
                product_id=product.product_id,
                cart_id=self.cart_id,
                quantity=quantity
            ).save()
            return cart_item

    def get_cart_items(self):
        return CartItem.objects.filter(cart_id=self, removed_at=None)


class CartItem(db.Document):
    cart_item_id = db.StringField(db_field="cart_item_id", primary_key=True)
    product_id = db.ReferenceField(Product, db_field="product_id")
    cart_id = db.ReferenceField(Cart, db_field="cart_id")
    quantity = db.IntField()
    added_at = db.DateTimeField(default=datetime.now())
    removed_at = db.DateTimeField()
    invoice_created_at = db.DateTimeField()

    meta = {
        'indexes': [("cart_id", "removed_at")]
    }