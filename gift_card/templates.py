from customer.templates import customer_obj


def gift_card_obj(gift_card):
    return {
        "gift_card_id": gift_card.gift_card_id,
        "original_balance_in_cents": gift_card.original_balance_in_cents,
        "current_balance_in_cents": gift_card.current_balance_in_cents,
        "created_at": gift_card.created_at,
        "updated_at": gift_card.updated_at,
        "gifter_customer": customer_obj(gift_card.gifter_customer),
        "recipient_customer": customer_obj(gift_card.recipient_customer),
        "links": {
            "gifter_customer": "/customer/" + gift_card.gifter_customer.customer_id,
            "recipient_customer": "/customer/" + gift_card.recipient_customer.customer_id
        }
    }
