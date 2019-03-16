def refund_object(refund):
    links = {
            "invoice": "/invoice/" + refund.invoice.invoice_id
    }

    if refund.credit is not None:
        links["credit"] = "/credit/" + refund.credit.credit_id

    return {
        "refund_id": refund.refund_id,
        "state": refund.state,
        "refund_line_items": refund_line_item_objects(refund.refund_line_items),
        "created_at": refund.created_at,
        "closed_at": refund.closed_at,
        "links": links
    }


def refund_line_item_object(refund_line_item):
    return {
        "refund_line_item_id": refund_line_item.refund_line_item_id,
        "invoice_line_item": refund_line_item.invoice_line_item,
        "total_amount_in_cents": refund_line_item.total_amount_in_cents,
        "tax_amount_in_cents": refund_line_item.tax_amount_in_cents
    }


def refund_line_item_objects(refund_line_items):
    obj_list = []
    for refund_line_item in refund_line_items:
        obj_list.append(refund_line_item_object(refund_line_item))
    return obj_list