schema = {
        "type": "object",
        "properties": {
            "currency":  {"type": "string"},
            "email":     {"type": "string"},
            "first_name": {"type": "string"},
            "last_name":  {"type": "string"},
            "addresses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "zip": {"type": "string"},
                        "state": {"type": "string"},
                        "country": {"type": "string"},
                        "is_primary": {"type": "string"},
                    }
                },
                "required": ["street", "city", "state", "country"]
            },
        },
        "required": ["currency", "email", "first_name", "last_name"]
}


address_schema = {
    "type": "object",
    "properties": {
            "street":      {"type": "string"},
            "city":        {"type": "string"},
            "zip":         {"type": "string"},
            "state":       {"type": "string"},
            "country":     {"type": "string"},
            "is_primary":  {"type": "string"},
        },
    "required": ["street", "city", "zip", "state", "country"]
}



