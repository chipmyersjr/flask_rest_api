from customer.models import Address


def customer_obj(customer):
    customer_data = {
      "customer_id": customer.customer_id,
      "currency": customer.currency,
      "email": customer.email,
      "first_name": customer.first_name,
      "last_name": customer.last_name,
      "total_spent": customer.total_spent,
      "last_order_date": customer.last_order_date,
      "created_at": customer.created_at,
      "updated_at": customer.updated_at,
      "deleted_at": customer.deleted_at,
      "links": [
            {"rel": "self", "href": "/customer/" + customer.customer_id}
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
