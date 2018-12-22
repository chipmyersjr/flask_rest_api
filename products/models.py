from application import db
from datetime import  datetime


class Product(db.Document):
    id = db.StringField(db_field="id")
    title = db.StringField(db_field="title")
    product_type = db.StringField(db_field="product_type")
    vendor = db.StringField(db_field="vendor")
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'indexes': ['id']
    }
