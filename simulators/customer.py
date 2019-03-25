import requests
from faker import Faker
from random import randint
import httplib2
import json


API_URL = "http://127.0.0.1/"


class Customer:

    def __init__(self):
        self.fake = Faker()
        self.customer_id = 0
        self.http = httplib2.Http()

        data = {
                  "app_id": "my_electronics_app",
                  "app_secret": "my_electronics_secret"
                }
        response = requests.post(url=API_URL + "store/token/", json=data)

        token = response.json().get('token')

        self.headers = {
            "APP-ID": "my_electronics_app",
            "ACCESS-TOKEN": token
        }

    def create(self):
        data = {
            "currency": "USD",
            "email": self.fake.email(),
            "first_name": self.fake.name().split(" ")[0],
            "last_name": self.fake.name().split(" ")[1],
            "password": "1234",
            "addresses":
                [
                    {
                        "street": self.fake.address(),
                        "city": self.fake.city(),
                        "zip": str(randint(1000, 99999)),
                        "state": self.fake.state(),
                        "country": self.fake.country(),
                        "is_primary": "true"
                    }
                ]
        }

        response = requests.post(url=API_URL + 'customer/', json=data, headers=self.headers).json()
        self.customer_id = response.get("customer")["customer_id"]

    def open_cart(self):
        return requests.post(url=API_URL + '/customer/' + str(self.customer_id) + '/cart', json=json.dumps("{}")
                             , headers=self.headers)

    def add_cart_item(self, product_id):
        data = {"quantity": randint(1, 5)}
        return requests.post(url=API_URL + 'customer/' + str(self.customer_id) + '/cart/item/' + product_id
                             , json=data, headers=self.headers)