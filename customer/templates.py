from datetime import datetime

from customer.models import Address


def customer_obj(customer):
    customer_data = {
      "customer_id": customer.customer_id,
      "currency": customer.currency,
      "email": customer.email,
      "first_name": customer.first_name,
      "last_name": customer.last_name,
      "total_spent": str(customer.total_spent),
      "last_order_date": customer.last_order_date,
      "last_cart_activity_at": customer.last_cart_activity_at,
      "last_cart_created_at": customer.last_cart_created_at,
      "created_at": customer.created_at,
      "updated_at": customer.updated_at,
      "deleted_at": customer.deleted_at,
      "logged_in": True if datetime.now() < customer.log_out_expires_at else False,
      "links": [
            {"rel": "self", "href": "/customer/" + customer.customer_id},
            {"rel": "cart", "href": "/customer/" + customer.customer_id + "/cart"}
        ]
    }

    addresses = Address.objects.filter(customer_id=customer).all()

    customer_data['addresses'] = addresses_obj(addresses)

    return customer_data


def address_obj(address):
    return {
        "address_id": address.address_id,
        "street": address.street,
        "city": address.city,
        "zip": address.zip,
        "state": address.state,
        "is_primary": address.is_primary,
        "created_at": address.created_at,
        "updated_at": address.updated_at,
        "deleted_at": address.deleted_at
    }


def addresses_obj(addresses):
    addresses_obj_list = []
    for address in addresses:
        addresses_obj_list.append(address_obj(address))
    return addresses_obj_list


def addresses_obj_for_pagination(addresses):
    addresses_obj_list = []
    for address in addresses.items:
        addresses_obj_list.append(address_obj(address))
    return addresses_obj_list


def customer_objs(customers):
    customer_obj_list = []
    for customer in customers.items:
        customer_obj_list.append(customer_obj(customer))
    return customer_obj_list
