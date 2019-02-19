from application import db
from datetime import datetime, timedelta
import uuid

from store.models import Store


class Customer(db.Document):
    customer_id = db.StringField(db_field="customer_id", primary_key=True)
    store_id = db.ReferenceField(Store, db_field="store_id")
    currency = db.StringField(db_field="currency")
    email = db.StringField(db_field="email")
    first_name = db.StringField(db_field="first_name")
    last_name = db.StringField(db_field="last_name")
    total_spent = db.DecimalField(db_field="total_spent", default=0)
    last_order_date = db.DateTimeField(db_field="last_order_date")
    last_cart_activity_at = db.DateTimeField(db_field="last_cart_activity_at")
    last_cart_created_at = db.DateTimeField(db_field="last_cart_created_at")
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField(default=datetime.now())
    deleted_at = db.DateTimeField()

    meta = {
        'indexes': ['customer_id']
    }

    @classmethod
    def get_customer(cls, customer_id, request):
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        return Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()

    def add_address(self, request, is_primary=False):
        """
        adds a new address based on request

        :param request: will pull data from flask request object
        :param is_primary: set new address to primary if true
        :return: address object
        """

        new_address = Address(
            address_id=str(uuid.uuid4().int),
            customer_id=self,
            street=request.json.get("street"),
            city=request.json.get("city"),
            zip=request.json.get("zip"),
            state=request.json.get("state"),
            country=request.json.get("country")
        ).save()

        if is_primary:
            new_address.make_primary()

        return new_address

    def get_primary_address(self):
        """

        :return: current primary address if exists
        """
        return Address.objects.filter(customer_id=self.customer_id, deleted_at=None, is_primary=True).first()

    def get_addresses(self):
        """

        :return: all not deleted customer addresses
        """
        return Address.objects.filter(customer_id=self.customer_id, deleted_at=None)


class Address(db.Document):
    address_id = db.StringField(db_field="address_id", primary_key=True, default=str(uuid.uuid4().int))
    customer_id = db.ReferenceField(Customer, db_field="customer_id")
    street = db.StringField(db_field="street")
    city = db.StringField(db_field="city")
    zip = db.StringField(db_field="zip")
    state = db.StringField(db_field="state")
    country = db.StringField(db_field="country")
    is_primary = db.BooleanField(db_field="is_primary", default=False)
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField(default=datetime.now())
    deleted_at = db.DateTimeField()

    def make_primary(self):
        """
        marks the address as primary. unmarks the old primary address

        :return: address obj
        """
        old_primary_address = Address.objects.filter(customer_id=self.customer_id, is_primary=True).first()

        if old_primary_address:
            old_primary_address.is_primary = False
            old_primary_address.updated_at = datetime.now()
            old_primary_address.save()

        self.is_primary = True
        self.updated_at = datetime.now()
        self.save()

    def delete(self):
        """
        marks an address as deleted

        :return: null
        """
        self.deleted_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_primary = False
        self.save()

    meta = {
        'indexes': [('customer_id', 'address_id')]
    }