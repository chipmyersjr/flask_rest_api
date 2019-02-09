from customer.templates import customer_obj


def credit_obj(credit):
    return {
        "credit_id": credit.credit_id,
        "customer": customer_obj(credit.customer),
        "original_balance_in_cents": credit.original_balance_in_cents,
        "current_balance_in_cents": credit.current_balance_in_cents,
        "created_at": credit.created_at,
        "updated_at": credit.updated_at,
        "voided_at": credit.voided_at,
        "links": {
            "customer": "/customer/" + credit.customer.customer_id
        }
    }


def credit_objs(credits):
    obj_list = []
    for credit in credits.items:
        obj_list.append(credit_obj(credit))
    return obj_list
