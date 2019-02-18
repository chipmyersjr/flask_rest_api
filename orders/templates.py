from product.templates import product_obj
from orders.models import OrderLineItem


def order_obj(order):
    order_line_items = OrderLineItem.objects.filter()

    return {
        "order_id": order.order_id,
        "status": order.status,
        "created_at": order.created_at,
        "shipped_at": order.shipped_at,
        "delivered_at": order.delivered_at,
        "canceled_at": order.canceled_at,
        "order_line_items": order_line_item_objs(order_line_items=order_line_items),
        "links": {
            "self": "/order/" + order.order_id,
            "invoice": "/invoice" + order.invoice.invoice_id,
            "shipped": "/order/" + order.order_id + "/shipped",
            "delivered": "/order/" + order.order_id + "/delivered",
            "canceled": "/order/" + order.order_id + "/canceled"
        }
    }


def order_line_item_obj(order_line_item):
    return {
        "order_line_item_id": order_line_item.order_line_item_id,
        "product": product_obj(order_line_item.product),
        "quantity": order_line_item.quantity
    }


def order_line_item_objs(order_line_items):
    obj_list = []
    for order_line_item in order_line_items:
        obj_list.append(order_line_item_obj(order_line_item))
    return obj_list


def order_objs(orders):
    obj_list = []
    for order in orders.items:
        obj_list.append(order_obj(order))
    return obj_list