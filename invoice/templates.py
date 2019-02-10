from product.templates import product_obj
from customer.templates import customer_obj
from cart.templates import cart_obj
from invoice.models import InvoiceLineItem


def invoice_obj(invoice):
    invoice_line_items = InvoiceLineItem.objects.filter(invoice=invoice).all()

    return {
        "invoice_id": invoice.invoice_id,
        "customer": customer_obj(invoice.customer),
        "cart": cart_obj(invoice.cart),
        "state": invoice.state,
        "gift_card_used_amount_in_cents": invoice.gift_card_used_amount_in_cents,
        "credit_used_amount_in_cents": invoice.credit_used_amount_in_cents,
        "total_amount_in_cents": invoice.get_total_amount(),
        "tax_amount_in_cents": invoice.get_tax_amount(),
        "subtotal_amount_in_cents": invoice.get_subtotal_amount(),
        "created_at": invoice.created_at,
        "closed_at": invoice.closed_at,
        "invoice_line_items": invoice_line_item_objs(invoice_line_items=invoice_line_items)
    }


def invoice_line_item_obj(invoice_line_item):
    return {
        "invoice_line_item_id": invoice_line_item.invoice_line_item_id,
        "product": product_obj(invoice_line_item.product),
        "quantity": invoice_line_item.quantity,
        "unit_amount_in_cents": invoice_line_item.unit_amount_in_cents,
        "total_amount_in_cents": invoice_line_item.total_amount_in_cents,
        "tax_amount_in_cents": invoice_line_item.tax_amount_in_cents,
        "type": invoice_line_item.type,
        "links": {
            "invoice": "/invoice/" + invoice_line_item.invoice.invoice_id,
            "product": "/product/" + invoice_line_item.product.product_id
        }
    }


def invoice_line_item_objs(invoice_line_items):
    obj_list = []
    for invoice_line_item in invoice_line_items:
        obj_list.append(invoice_line_item_obj(invoice_line_item))
    return obj_list