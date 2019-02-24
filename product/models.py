from application import db
from datetime import datetime
import uuid

from store.models import Store
from utils import DuplicateDataError


class ProductInventoryLessThanZeroException(Exception):
    pass


class ProductTag(db.EmbeddedDocument):
    product_tag_id = db.StringField(primary_key=True)
    tag = db.StringField()
    created_at = db.DateTimeField(default=datetime.now())
    deleted_at = db.DateTimeField()


class Product(db.Document):
    product_id = db.StringField(db_field="id", primary_key=True)
    title = db.StringField(db_field="title")
    product_type = db.StringField(db_field="product_type")
    description = db.StringField()
    vendor = db.StringField(db_field="vendor")
    store = db.ReferenceField(Store, db_field="store_id")
    inventory = db.IntField(db_field="inventory", default=0)
    sale_price_in_cents = db.IntField()
    tags = db.ListField(db.EmbeddedDocumentField(ProductTag))
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

    def add_tag(self, new_tag):
        """
        adds a new tag to product

        :param new_tag: new tag
        :return: null
        """
        if new_tag in [tag.tag for tag in self.tags]:
            raise DuplicateDataError

        new_tag_object = ProductTag(product_tag_id=str(uuid.uuid4().int), tag=new_tag)

        self.tags.append(new_tag_object)
        self.updated_at = datetime.now()
        self.save()

    def get_tags(self):
        """
        return list of active tags

        :return: list of tag objects
        """
        active_tags = []
        for tag in self.tags:
            if tag.deleted_at is None:
                active_tags.append(tag)

        return active_tags

    def delete_tags(self, tag_to_delete):
        """
        deletes one or all tags

        :param tag_to_delete: tag to be deleted
        :return: list of tag objects
        """
        deleted_tags = []
        for tag in self.tags:
            if tag.deleted_at is None and (tag.tag == tag_to_delete or tag_to_delete is None):
                tag.deleted_at = datetime.now()
                deleted_tags.append(tag)

        self.save()
        return deleted_tags
