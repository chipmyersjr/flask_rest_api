from application import db
from datetime import datetime, timedelta
import uuid


class Store(db.Document):
    store_id = db.StringField(db_field="id", primary_key=True, default=str(uuid.uuid4().int))
    name = db.StringField(db_field="name")
    tagline = db.StringField(db_field="tagline")
    app_id = db.StringField(db_field="app_id")
    app_secret = db.StringField(db_field="app_secret")
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField(default=datetime.now())
    deleted_at = db.DateTimeField()

    meta = {
        'indexes': ['store_id']
    }


class AccessToken(db.Document):
    store_id = db.ReferenceField(Store, db_field="store_id")
    token = db.StringField(db_field="name", default=str(uuid.uuid4().int))
    expires_at = db.DateTimeField(default=datetime.now() + timedelta(hours=24))
    created_at = db.DateTimeField(default=datetime.now())

    meta = {
        'indexes': ['store_id']
    }
