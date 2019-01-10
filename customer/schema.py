schema = {
        "type": "object",
        "properties": {
            "currency":  {"type": "string"},
            "email":     {"type": "string"},
            "firstname": {"type": "string"},
            "lastname":  {"type": "string"},
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
            "required": ["currency", "email", "firstname", "lastname"]
        }
}



