import requests
from faker import Faker
from random import randint, choice
import httplib2


API_URL = "http://127.0.0.1/"


class Admin:

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

    def create_product(self):
        vendors = ["Sony", "Nintendo", "Ubisoft", "Microsoft", "Bethesda"]
        product_types = ["Console", "Game"]

        data = {
            "title": self.fake.words()[0],
            "product_type": choice(product_types),
            "vendor": choice(vendors),
            "inventory": randint(0, 1000),
            "sale_price_in_cents": randint(500, 10000),
            "description": self.fake.sentence(randint(5, 15))
        }

        return requests.post(url=API_URL + 'product/', json=data, headers=self.headers).json()