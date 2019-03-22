schema = {
    "type": "array",
    "items": {
            "type": "object",
            "properties": {
                    "invoice_line_item_id": {"type": "string"},
                    "amount_in_cents": {"type": "string"}
            }
    },
    "required": ["invoice_line_item_id"]
}