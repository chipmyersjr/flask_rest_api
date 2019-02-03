create_gift_cart_schema = {
    "type": "object",
    "properties": {
        "gifter_customer_id":  {"type": "string"},
        "recipient_customer_id": {"type": "string"},
        "original_amount":    {"type": "integer"}
    },
    "required": ["gifter_customer_id", "recipient_customer_id", "original_amount"]
}
