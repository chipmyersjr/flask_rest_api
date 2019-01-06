schema = {
    "type": "object",
    "properties": {
        "name":        {"type": "string"},
        "tagline":     {"type": "string"},
        "app_id":      {"type": "string"},
        "app_secret":  {"type": "string"},
    },
    "required": ["name", "app_id", "app_secret"]
}


token_request_schema = {
    "type": "object",
    "properties": {
        "app_id":      {"type": "string"},
        "app_secret":  {"type": "string"},
    },
    "required": ["app_id", "app_secret"]
}