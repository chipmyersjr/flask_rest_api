remove_multiple_items_schema = {
            "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string"}
                    }
                },
            "required": ["product_id"]
}


put_cart_schema = {
    "type": "object",
    "properties": {
        "quantity": {"type": "integer"}
    },
    "required": ["quantity"]
}