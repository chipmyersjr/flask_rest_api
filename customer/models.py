from application import db
from datetime import datetime, timedelta
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, url_for
from flask_mail import Message
import os


from store.models import Store
from utils import DuplicateDataError
from kafka_server.decorators import produces_kafka_message
from application import mail


MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")


class Email(db.EmbeddedDocument):
    email_id = db.StringField(primary_key=True)
    email = db.StringField()
    is_primary = db.BooleanField(db_field="is_primary", default=False)
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField()
    deleted_at = db.DateTimeField()


@produces_kafka_message.apply
class Customer(db.Document):
    customer_id = db.StringField(db_field="customer_id", primary_key=True)
    password_hash = db.StringField()
    store_id = db.ReferenceField(Store, db_field="store_id")
    currency = db.StringField(db_field="currency")
    email = db.StringField(db_field="email")
    first_name = db.StringField(db_field="first_name")
    last_name = db.StringField(db_field="last_name")
    total_spent = db.DecimalField(db_field="total_spent", default=0)
    last_order_date = db.DateTimeField(db_field="last_order_date")
    last_cart_activity_at = db.DateTimeField(db_field="last_cart_activity_at")
    last_cart_created_at = db.DateTimeField(db_field="last_cart_created_at")
    log_out_expires_at = db.DateTimeField(default=datetime.now())
    emails = db.ListField(db.EmbeddedDocumentField(Email))
    confirmed_on = db.DateTimeField()
    confirmation_token = db.StringField()
    confirmation_token_expires_at = db.DateTimeField()
    created_at = db.DateTimeField(default=datetime.now())
    updated_at = db.DateTimeField(default=datetime.now())
    deleted_at = db.DateTimeField()

    meta = {
        'indexes': [('customer_id', ), ('email', )]
    }

    @classmethod
    def get_customer(cls, customer_id, request):
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        return Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()

    @classmethod
    def get_customer_by_email(cls, email, request):
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        return Customer.objects.filter(email=email, store_id=store, deleted_at=None).first()

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

    def set_password(self, password):
        """
        creates password for user

        :param password: new password
        :return: null
        """
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password):
        """
        checks if customer password is correct

        :param password: password to check
        :return: boolean
        """
        return check_password_hash(self.password_hash, password)

    def login(self):
        """
        logs customer in

        :return: null
        """
        self.log_out_expires_at = datetime.now() + timedelta(hours=24)
        self.save()

    def logout(self):
        """
        logs customer out

        :return: null
        """
        self.log_out_expires_at = datetime.now()
        self.save()

    def add_email(self, new_email, is_primary=False):
        """
        adds a new email

        :param new_email: new email address
        :param is_primary: true if new email address should
        :return: null
        """
        for email in self.emails:
            if is_primary:
                email.is_primary = False
            if email.email == new_email and email.deleted_at is None:
                raise DuplicateDataError

        new_email_document = Email(email_id=str(uuid.uuid4().int), email=new_email, is_primary=is_primary)

        if is_primary:
            self.email = new_email
            self.updated_at = datetime.now()

        self.emails.append(new_email_document)
        self.save()

    def get_emails(self):
        """
        return list of active emails

        :return: list of email objects
        """
        active_emails = []
        for email in self.emails:
            if email.deleted_at is None:
                active_emails.append(email)

        return active_emails

    def delete_email(self, email_to_delete):
        """
        deletes a customer email

        :param email_to_delete: email to be deleted
        :return: email object
        """
        for email in self.emails:
            if email.email == email_to_delete and email.deleted_at is None:
                email.deleted_at = datetime.now()
                email.updated_at = datetime.now()
                self.updated_at = datetime.now()
                self.save()
                return email

        return None

    def make_email_primary(self, new_primay_email):
        if new_primay_email not in [email.email for email in self.emails]:
            return None

        new_primay_email_object = None
        for email in self.emails:
            if email.email == new_primay_email:
                email.is_primary = True
                new_primay_email_object = email
            else:
                email.is_primary = False

        self.save()
        return new_primay_email_object

    def send_email(self, subject, body):
        """
        sends an email to the customers primary email

        :return: none
        """
        msg = Message(subject,
                      sender="store.app.api@gmail.com",
                      recipients=[self.email])
        msg.html = body
        mail.send(msg)

    def send_confirmation(self):
        """
        sends confirmation email

        :return: none
        """
        self.confirmation_token = str(uuid.uuid4().int)
        self.confirmation_token_expires_at = datetime.now() + timedelta(hours=24)
        self.save()

        subject = "Store Confirmation"
        link = "localhost/customer/confirm/" + self.confirmation_token
        html = "<html>Please click the link to confirm your registration: <a href={}>link</a></html>".format(link)
        self.send_email(subject=subject, body=html)


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
    updated_at = db.DateTimeField()
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
        'indexes': [('customer_id', ), ('address_id', )]
    }