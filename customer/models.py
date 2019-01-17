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
    last_order_date = db.StringField(db_field="last_order_date")
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField(default=datetime.now())
    deleted_at = db.DateTimeField()

    meta = {
        'indexes': ['customer_id']
    }


class Address(db.Document):
    address_id = db.StringField(db_field="address_id", primary_key=True, default=str(uuid.uuid4().int))
    customer_id = db.ReferenceField(Customer, db_field="customer_id")
    street = db.StringField(db_field="street")
    city = db.StringField(db_field="city")
    zip = db.StringField(db_field="zip")
    state = db.StringField(db_field="state")
    country = db.StringField(db_field="country")
    is_primary = db.BooleanField(db_field="is_primary")
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField(default=datetime.now())
    deleted_at = db.DateTimeField()

    meta = {
        'indexes': [('customer_id', 'address_id')]
    }