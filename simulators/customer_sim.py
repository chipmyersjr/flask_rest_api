import requests
from faker import Faker
from random import randint
import httplib2
import json

API_URL = "http://127.0.0.1/"


class CustomerSim:

    def __init__(self):
        self.fake = Faker()
        self.customer_id = None
        self.http = httplib2.Http()
        self.email = None
        self.password = "1234"

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
            "password": self.password,
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
        self.email = response.get("customer")["email"]

        data = {
            "password": "1234",
            "email": self.email
        }
        requests.put(url=API_URL + 'customer/login', json=data, headers=self.headers).json()

        self.confirm()

    def open_cart(self):
        self.refresh_token()

        return requests.post(url=API_URL + 'customer/' + str(self.customer_id) + '/cart', json=json.dumps("{}")
                             , headers=self.headers)

    def add_cart_item(self, product_id):
        self.refresh_token()

        data = {"quantity": randint(1, 5)}
        return requests.post(url=API_URL + 'customer/' + str(self.customer_id) + '/cart/item/' + product_id
                             , json=data, headers=self.headers)

    def refresh_token(self):
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

    def confirm(self):
        response = requests.put(url=API_URL + 'customer/' + self.customer_id + '/send_confirmation'
                                 , headers=self.headers).json()

        token = response.get("result")

        requests.get(url=API_URL + 'customer/confirm/' + token, headers=self.headers)