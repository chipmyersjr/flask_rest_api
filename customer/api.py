from flask.views import MethodView
from flask import jsonify, request, abort
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
import uuid
from datetime import datetime

from store.models import Store
from store.decorators import token_required
from customer.schema import schema, address_schema
from customer.models import Customer, Address
from customer.templates import customer_obj, customer_objs, address_obj, addresses_obj_for_pagination
from utils import paginated_results, DuplicateDataError

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
ADDRESS_NOT_FOUND = "ADDRESS_NOT_FOUND"
INCORRECT_PASSWORD = "INCORRECT_PASSWORD"
MISSING_CRENDENTIALS = "MISSING_CRENDENTIALS"
EMAIL_IS_REQUIRED_FIELD = "EMAIL_IS_REQUIRED_FIELD"


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
            customers = Customer.objects.filter(store_id=store, deleted_at=None)
            return paginated_results(objects=customers, collection_name='customer', request=request
                                     , per_page=self.PER_PAGE, serialization_func=customer_objs), 200

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
        existing_customer = Customer.objects.filter(email=customer_json.get("email"), store_id=store).first()

        if existing_customer:
            return jsonify({"error": "CUSTOMER_ALREADY_EXISTS"}), 400

        count_is_primary = 0
        if customer_json.get("addresses"):
            for address in customer_json.get("addresses"):
                if address.get("is_primary"):
                    if address.get("is_primary") == "true":
                        count_is_primary += 1
                        if count_is_primary > 1:
                            return jsonify({"error": "MULTIPLE_PRIMARY_ADDRESSES_SUPPLIED"}), 400

        customer = Customer(
            currency=customer_json.get("currency"),
            email=customer_json.get("email"),
            first_name=customer_json.get("first_name"),
            last_name=customer_json.get("last_name"),
            customer_id=str(uuid.uuid4().int),
            store_id=store
        ).save()

        customer.set_password(customer_json.get("password"))

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
        else:
            customer.updated_at = datetime.now()
            customer.save()

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


class CustomerCountAPI(MethodView):
    @token_required
    def get(self):
        """
        Returns a count of all customers for current store

        Endpoint = /customer/count/

        Example response:
        {
          "count": "20",
          "result": "ok"
        }
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()
        response = {
            "result": "ok",
            "count": str(Customer.objects.filter(store_id=store, deleted_at=None).count())
        }
        return jsonify(response), 200


class CustomerAddressAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def get(self, customer_id):
        """
        return primary address or list of all addresses

        :param customer_id: to return list of addresses for
        :return: addresses
        """
        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        if request.args.get("is_primary"):
            if request.args.get("is_primary").lower() == "true":
                response = {
                    "result": "ok",
                    "address": address_obj(customer.get_primary_address())
                }
                return jsonify(response), 200

        return paginated_results(objects=customer.get_addresses(), collection_name='address', request=request
                                 , per_page=self.PER_PAGE, serialization_func=addresses_obj_for_pagination), 200

    @token_required
    def post(self, customer_id):
        """
        creates a new customer address. Overrides primary if is_primary included in request

        :param customer_id: customer whose address to be added to
        :return: address object
        """

        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        error = best_match(Draft4Validator(address_schema).iter_errors(request.json))
        if error:
            return jsonify({"error": error.message}), 400

        if request.json.get("is_primary") is not None:
            if request.json.get("is_primary").lower() == "true":
                response = {
                    "result": "ok",
                    "address": address_obj(customer.add_address(request=request, is_primary=True))
                }
                return jsonify(response), 201

        return jsonify(address_obj(customer.add_address(request=request, is_primary=False))), 201

    @token_required
    def put(self, customer_id, address_id):
        """
        switch primary address

        :param customer_id: customer to update
        :param address_id: address to become primary
        :return: address object
        """

        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        address = customer.get_addresses().filter(address_id=address_id).first()

        if address is None:
            return jsonify({"error": ADDRESS_NOT_FOUND}), 404

        address.make_primary()

        response = {
            "result": "ok",
            "address": address_obj(address)
        }
        return jsonify(response), 200

    @token_required
    def delete(self, customer_id, address_id):
        """
        deletes an address

        :param customer_id: customer to be updated
        :param address_id: address to be delete
        :return: null
        """

        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        address = customer.get_addresses().filter(address_id=address_id).first()

        if address is None:
            return jsonify({"error": ADDRESS_NOT_FOUND}), 404

        address.delete()

        return jsonify({}), 204


class CustomerLogin(MethodView):

    @token_required
    def put(self):
        """
        logs customer in by providing email and password

        :return: customer object
        """
        if request.json.get("password") is None or request.json.get("email") is None:
            return jsonify({"error": MISSING_CRENDENTIALS}), 403

        customer = Customer.get_customer_by_email(email=request.json.get("email"), request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        if customer.check_password(request.json.get("password")):
            customer.login()
            response = {
                "result": "ok",
                "customer": customer_obj(customer)
            }
            return jsonify(response), 200

        return jsonify({"error": INCORRECT_PASSWORD}), 403


class CustomerLogOut(MethodView):

    @token_required
    def put(self):
        """
        logs customer out by providing email

        :return: customer
        """
        if request.json.get("email") is None:
            return jsonify({"error": MISSING_CRENDENTIALS}), 403

        customer = Customer.get_customer_by_email(email=request.json.get("email"), request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        customer.logout()

        response = {
            "result": "ok",
            "customer": customer_obj(customer)
        }
        return jsonify(response), 200


class CustomerEmailAPI(MethodView):

    @token_required
    def post(self, customer_id):
        """
        creates a new email

        query_parameters: is_primary

        :param customer_id: customer to be updated
        :return: customer object
        """
        if request.json.get("email") is None:
            return jsonify({"error": EMAIL_IS_REQUIRED_FIELD}), 403

        customer = Customer.get_customer(customer_id=customer_id, request=request)

        is_primary = False
        if request.args.get("is_primary") is not None:
            if request.args.get("is_primary").lower() == "true":
                is_primary = True

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        try:
            customer.add_email(new_email=request.json.get("email"), is_primary=is_primary)
        except DuplicateDataError:
            response = {
                "result": "already exists",
                "customer": customer_obj(customer)
            }
            return jsonify(response), 303

        response = {
            "result": "ok",
            "customer": customer_obj(customer)
        }
        return jsonify(response), 201

    @token_required
    def delete(self, customer_id):
        """
        deletes an email

        query_parameters: is_primary

        :param customer_id: customer to be updated
        :return: customer object
        """
        if request.json.get("email") is None:
            return jsonify({"error": EMAIL_IS_REQUIRED_FIELD}), 403

        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        deleted_email = customer.delete_email(email_to_delete=request.json.get("email"))

        if deleted_email is None:
            response = {
                "result": "not found",
                "customer": customer_obj(customer)
            }
            return jsonify(response), 404

        response = {
            "result": "ok",
            "customer": customer_obj(customer)
        }
        return jsonify(response), 204

    @token_required
    def put(self, customer_id):
        """
        marks email address as primary

        :param customer_id: customer to be updated
        :return: customer object
        """
        if request.json.get("email") is None:
            return jsonify({"error": EMAIL_IS_REQUIRED_FIELD}), 403

        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        new_primary_email = customer.make_email_primary(new_primay_email=request.json.get("email"))

        if new_primary_email is None:
            response = {
                "result": "not found",
                "customer": customer_obj(customer)
            }
            return jsonify(response), 404

        response = {
            "result": "ok",
            "customer": customer_obj(customer)
        }
        return jsonify(response), 200
