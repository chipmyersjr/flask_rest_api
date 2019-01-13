from flask.views import MethodView
from flask import jsonify, request, abort
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
import uuid
from datetime import datetime

from store.models import Store
from store.decorators import token_required
from customer.schema import schema
from customer.models import Customer, Address
from customer.templates import customer_obj


class CustomerAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def get(self, customer_id=None):
        """
        Gets a customer by providing customer_id

        Endpoint: /customer/209485626598208918917359936593901836672

        Example Response:

        {
            "customer": {
                "addresses": [
                    {
                        "address_id": "160725188092123457335884996198595450510",
                        "city": "townsville",
                        "created_at": "Sun, 13 Jan 2019 19:48:27 GMT",
                        "deleted_at": null,
                        "is_primary": true,
                        "state": "CA",
                        "street": "1236 Main Street",
                        "updated_at": "Sun, 13 Jan 2019 19:48:27 GMT",
                        "zip": "1234"
                    }
                ],
                "created_at": "Sun, 13 Jan 2019 19:48:27 GMT",
                "currency": "USD",
                "customer_id": "209485626598208918917359936593901836672",
                "deleted_at": null,
                "email": "johnsmith@gmail.com",
                "first_name": "John",
                "last_name": "Smith4",
                "last_order_date": null,
                "links": [
                    {
                        "href": "/customer/209485626598208918917359936593901836672",
                        "rel": "self"
                    }
                ],
                "total_spent": "0.00",
                "updated_at": "Sun, 13 Jan 2019 19:48:27 GMT"
            },
            "result": "ok"
        }
        """

        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        if customer_id:
            customer = Customer.objects.filter(customer_id=customer_id, deleted_at=None, store_id=store).first()
            if customer:
                response = {
                    "result": "ok",
                    "customer": customer_obj(customer)
                }
                return jsonify(response), 200
            else:
                return jsonify({}), 404
        else:
            href = "/product/?page=%s"

    @token_required
    def post(self):
        """
        Creates a new customer

        Endpoint: /customer/

        Example Post Body:
        {
            "currency": "USD",
            "email": "johnsmith@gmail.com",
            "first_name": "John",
            "last_name": "Smith4",
            "addresses":
              [
                    {
                          "street": "1236 Main Street",
                          "city": "townsville",
                          "zip": "1234",
                          "state": "CA",
                          "country": "USA",
                          "is_primary": "true"
                    },
                    {
                          "street": "1215 Main Street",
                          "city": "townsville",
                          "zip": "500",
                          "state": "CA",
                          "country": "USA"
                    },
                    {
                          "street": "1216 Main Street",
                          "city": "townsville",
                          "zip": "500",
                          "state": "CA",
                          "country": "USA"
                    }
              ]
        }

        {
             "customer": {
                 "addresses": [
                     {
                         "address_id": "224473682041851492125327501325163956867",
                         "city": "townsville",
                         "created_at": "Thu, 10 Jan 2019 03:56:26 GMT",
                         "deleted_at": null,
                         "is_primary": false,
                         "state": "CA",
                         "street": "1215 Main Street",
                         "updated_at": "Thu, 10 Jan 2019 03:56:26 GMT",
                         "zip": "500"
                     },
                     {
                         "address_id": "245608141370371202915656949519861248348",
                         "city": "townsville",
                         "created_at": "Thu, 10 Jan 2019 03:56:26 GMT",
                         "deleted_at": null,
                         "is_primary": true,
                         "state": "CA",
                         "street": "1236 Main Street",
                         "updated_at": "Thu, 10 Jan 2019 03:56:26 GMT",
                         "zip": "1234"
                     },
                     {
                         "address_id": "274242069278329272621665758252140893540",
                         "city": "townsville",
                         "created_at": "Thu, 10 Jan 2019 03:56:26 GMT",
                         "deleted_at": null,
                         "is_primary": false,
                         "state": "CA",
                         "street": "1216 Main Street",
                         "updated_at": "Thu, 10 Jan 2019 03:56:26 GMT",
                         "zip": "500"
                     }
                 ],
                 "created_at": "Thu, 10 Jan 2019 03:56:26 GMT",
                 "currency": "USD",
                 "customer_id": "204987158183621343381078484949153439747",
                 "deleted_at": null,
                 "email": "johnsmith@gmail.com",
                 "first_name": "John",
                 "last_name": "Smith4",
                 "last_order_date": null,
                 "links": [
                     {
                         "href": "/customer/204987158183621343381078484949153439747",
                         "rel": "self"
                     }
                 ],
                 "total_spent": 0,
                 "updated_at": "Thu, 10 Jan 2019 03:56:26 GMT"
             },
        "result": "ok"
        }
        """
        customer_json = request.json
        error = best_match(Draft4Validator(schema).iter_errors(customer_json))
        if error:
            return jsonify({"error": error.message}), 400

        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()
        customer = Customer(
            currency=customer_json.get("currency"),
            email=customer_json.get("email"),
            first_name=customer_json.get("first_name"),
            last_name=customer_json.get("last_name"),
            store_id=store
        ).save()

        if customer_json.get("addresses"):
            addresses = []
            for address in customer_json.get("addresses"):
                is_primary = False
                if address.get("is_primary"):
                    is_primary = True if address.get("is_primary").lower() == "true" else False
                address = Address(
                    street=address.get("street"),
                    city=address.get("city"),
                    zip=address.get("zip"),
                    state=address.get("state"),
                    country=address.get("country"),
                    is_primary=is_primary,
                    customer_id=customer,
                    address_id=str(uuid.uuid4().int)
                )
                addresses.append(address)

            for add in addresses:
                Address.objects.insert(add)

        response = {
            "result": "ok",
            "customer": customer_obj(customer)
        }
        return jsonify(response), 201

    @token_required
    def put(self, customer_id):
        """
        update one or more customer fields

        Endpoint: /customer/209485626598208918917359936593901836672

        Example Post Body:
        {
           "currency": "GBR"
        }

        Example Response:
        {
            "customer": {
                "addresses": [
                    {
                        "address_id": "160725188092123457335884996198595450510",
                        "city": "townsville",
                        "created_at": "Sun, 13 Jan 2019 19:48:27 GMT",
                        "deleted_at": null,
                        "is_primary": true,
                        "state": "CA",
                        "street": "1236 Main Street",
                        "updated_at": "Sun, 13 Jan 2019 19:48:27 GMT",
                        "zip": "1234"
                    }
                ],
                "created_at": "Sun, 13 Jan 2019 19:48:27 GMT",
                "currency": "GBR",
                "customer_id": "209485626598208918917359936593901836672",
                "deleted_at": null,
                "email": "johnsmith@gmail.com",
                "first_name": "John",
                "last_name": "Smith4",
                "last_order_date": null,
                "links": [
                    {
                        "href": "/customer/209485626598208918917359936593901836672",
                        "rel": "self"
                    }
                ],
                "total_spent": "0.00",
                "updated_at": "Sun, 13 Jan 2019 19:48:27 GMT"
            },
            "result": "ok"
        }
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        customer = Customer.objects.filter(customer_id=customer_id, deleted_at=None, store_id=store).first()
        if not customer:
            return jsonify({}), 404

        customer_json = request.json

        items_updated = 0
        if customer_json.get("currency"):
            customer.currency = customer_json.get("currency")
            items_updated += 1

        if customer_json.get("email"):
            customer.email = customer_json.get("email")
            items_updated += 1

        if customer_json.get("first_name"):
            customer.first_name = customer_json.get("first_name")
            items_updated += 1

        if customer_json.get("last_name"):
            customer.first_name = customer_json.get("last_name")
            items_updated += 1

        if items_updated == 0:
            return jsonify({"error": "No fields supplied for update"}), 400

        response = {
            "result": "ok",
            "customer": customer_obj(customer)
        }
        return jsonify(response), 201

    @token_required
    def delete(self, customer_id):
        """
        delete a specific product by providing product id

        Endpoint: /product/88517737685737189039085760589870132011
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()
        customer = Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()
        if not customer:
            return jsonify({}), 404
        customer.deleted_at = datetime.now()
        customer.save()

        return jsonify({}), 204
