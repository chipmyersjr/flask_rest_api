from functools import wraps
from flask import jsonify

from customer.models import Customer

CUSTOMER_NOT_FOUND = "CUSTOMER_NOT_FOUND"
CUSTOMER_IS_NOT_CONFIRMED = "CUSTOMER_IS_NOT_CONFIRMED"


def customer_confirmation_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        customer = Customer.objects.filter(customer_id=kwargs["customer_id"]).first()

        if customer is None:
            if customer is None:
                return jsonify({"error": CUSTOMER_NOT_FOUND}), 404

        if customer.confirmed_on is None:
            return jsonify({"error": CUSTOMER_IS_NOT_CONFIRMED}), 403
        return f(*args, **kwargs)
    return decorated_function