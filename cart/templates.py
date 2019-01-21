def cart_obj(cart):
    return {
        "cart_id": cart.cart_id,
        "state": cart.state,
        "created_at": cart.created_at,
        "last_item_added_at": cart.last_item_added_at,
        "invoice_created_at": cart.invoice_created_at,
        "closed_at": cart.closed_at,
        "deleted_at": cart.deleted_at
    }