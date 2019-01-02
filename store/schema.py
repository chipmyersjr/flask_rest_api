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