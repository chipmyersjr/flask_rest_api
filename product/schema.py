schema = {
    "type": "object",
    "properties": {
        "title":        {"type": "string"},
        "product_type": {"type": "string"},
        "vendor":       {"type": "string"},
        "inventory":    {"type": "integer"}
    },
    "required": ["title", "product_type", "vendor"]
}
