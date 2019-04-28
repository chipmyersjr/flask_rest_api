from flask.views import MethodView
from flask import request, jsonify, abort
import uuid
import os
import pymongo
from rq.job import Job
from rq.exceptions import NoSuchJobError
from worker import conn
from datetime import datetime
from time import sleep

from store.decorators import token_required
from store.models import Store
from customer.models import Customer
from credit.models import Credit
from credit.templates import credit_obj, credit_objs
from utils import paginated_results
from application import redis_task_queue

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
AMOUNT_SHOULD_BE_INT = "AMOUNT_SHOULD_BE_INT"
CREDIT_NOT_FOUND = "CREDIT_NOT_FOUND"


class CustomerCreditAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    @token_required
    def get(self, customer_id):
        """
        returns a list of customer credits

        params:
        active (true only includes credits with balance more that zero)
        """
        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        credits = Credit.objects.filter(customer=customer)

        if "active" in request.args:
            if request.args['active'].lower() == 'true':
                credits = credits.filter(current_balance_in_cents__gt=0)

        return paginated_results(objects=credits, collection_name='credit', request=request
                                 , per_page=self.PER_PAGE, serialization_func=credit_objs), 200

    @token_required
    def post(self, customer_id, amount):
        """
        issue a credit to a customer

        :param customer_id: customer to add credit to
        :param amount: amount of credit to be given
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        customer = Customer.objects.filter(customer_id=customer_id, store_id=store, deleted_at=None).first()

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        try:
            amount = int(amount)
        except ValueError:
            return jsonify({"error": AMOUNT_SHOULD_BE_INT}), 400

        credit = Credit(
            credit_id=str(uuid.uuid4().int),
            customer=customer,
            original_balance_in_cents=amount,
            current_balance_in_cents=amount
        ).save()

        response = {
            "result": "ok",
            "credit": credit_obj(credit)
        }
        return jsonify(response), 201

    @token_required
    def delete(self, customer_id, credit_id):
        """
        voids a credit

        :param credit_id: credit to be voided
        :param customer_id: customer whose credit is to be voided
        """
        customer = Customer.get_customer(customer_id=customer_id, request=request)

        if customer is None:
            return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        credit = Credit.objects.filter(customer=customer, credit_id=credit_id).first()

        if credit is None:
            return jsonify({"error": CREDIT_NOT_FOUND}), 404

        credit.void_credit()

        return jsonify({}), 204


class CustomerBatchCreditAPI(MethodView):

    def __init__(self):
        self.PER_PAGE = 10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def get(self, job_id):
        """
        returns status of credit batch job

        :return: boolean
        """
        try:
            job = Job.fetch(job_id, connection=conn)
        except NoSuchJobError:
            return jsonify({"result": "job not found"}), 404

        if job.is_finished:
            return jsonify({"result": str(job.result)}), 200
        else:
            return jsonify({"result": "complete"}), 202

    def post(self, amount):
        """
        send batch credit create to redis job queue

        :return: job id
        """
        try:
            amount = int(amount)
        except ValueError:
            return jsonify({"error": AMOUNT_SHOULD_BE_INT}), 400

        job = redis_task_queue.enqueue_call(func=self.batch_create_credit, args=(request.headers.get('APP-ID'), amount,)
                                            , result_ttl=50000)

        response = {
            "result": "ok",
            "job_id": job.get_id()
        }
        return jsonify(response), 201

    @classmethod
    def batch_create_credit(cls, APP_ID, amount):
        """
        batch create customer credits

        :return: null
        """
        client = pymongo.MongoClient("mongodb://" + os.environ.get("MONGODB_HOST") + ":27017/")
        db = client["store"]
        customer_collection = db["customer"]
        store_collection = db["store"]
        credit_collection = db["credit"]

        store = store_collection.find_one({"app_id": APP_ID}, {"_id": 1})

        credits = []
        for customer in customer_collection.find({"store_id": store["_id"]}, {"_id": 1, "deleted_at": 1}):
            if "deleted_at" not in customer:
                credit = {
                    "credit_id": str(uuid.uuid4().int),
                    "customer_id": customer["_id"],
                    "original_balance_in_cents": amount,
                    "current_balance_in_cents": amount,
                    "created_at": datetime.now()
                }
                credits.append(credit)

        credit_collection.insert_many(credits)
