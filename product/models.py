from application import db
from datetime import datetime

from store.models import Store


class Product(db.Document):
    product_id = db.StringField(db_field="id", primary_key=True)
    title = db.StringField(db_field="title")
    product_type = db.StringField(db_field="product_type")
    vendor = db.StringField(db_field="vendor")
    store = db.ReferenceField(Store, db_field="store_id")
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField(default=datetime.now())
    deleted_at = db.DateTimeField()

    meta = {
        'indexes': ['id']
    }
