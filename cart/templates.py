from cart.models import CartItem


def cart_obj(cart):
    cart_data = {
        "cart_id": cart.cart_id,
        "state": cart.state,
        "created_at": cart.created_at,
        "last_item_added_at": cart.last_item_added_at,
        "invoice_created_at": cart.invoice_created_at,
        "closed_at": cart.closed_at,
        "links": [
            {"rel": "self", "href": "/customer/" + cart.customer_id.customer_id + "/cart"},
            {"rel": "customer", "href": "/customer/" + cart.customer_id.customer_id}
        ]
    }

    cart_items = CartItem.objects.filter(cart_id=cart.cart_id, removed_at=None).all()

    cart_data['items'] = cart_items_obj(cart_items)

    return cart_data


def cart_item_obj(cart_item):
    return {
        "cart_item_id": cart_item.cart_item_id,
        "product_id": cart_item.product_id.product_id,
        "product_title": cart_item.product_id.product_title,
        "product_vendor": cart_item.product_id.vendor,
        "product_type": cart_item.product_id.product_type,
        "added_at": cart_item.added_at
    }


def cart_items_obj(cart_items):
    cart_items_obj_list = []
    for cart_item in cart_items:
        cart_items_obj_list.append(cart_item_obj(cart_item))
    return cart_items_obj_list
