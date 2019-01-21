from application import db
from datetime import datetime

from store.models import Store


class ProductInventoryLessThanZeroException(Exception):
    pass


class Product(db.Document):
    product_id = db.StringField(db_field="id", primary_key=True)
    title = db.StringField(db_field="title")
    product_type = db.StringField(db_field="product_type")
    vendor = db.StringField(db_field="vendor")
    store = db.ReferenceField(Store, db_field="store_id")
    inventory = db.IntField(db_field="inventory", default=0)
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField(default=datetime.now())
    deleted_at = db.DateTimeField()

    meta = {
        'indexes': [('id', 'store', 'deleted_at'), ('vendor', 'product_type', 'store', 'deleted_at')
                    , ('product_type', 'store', 'deleted_at'), ('vendor', 'store', 'deleted_at')]
    }

    def adjust_inventory(self, amount):
        new_amount = amount + self.inventory
        if new_amount < 0:
            raise ProductInventoryLessThanZeroException
        self.inventory = new_amount
        self.save()

    def set_inventory(self, amount):
        if amount < 0:
            raise ProductInventoryLessThanZeroException
        self.inventory = amount
        self.save()