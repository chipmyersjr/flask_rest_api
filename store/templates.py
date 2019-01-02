def store_obj(store):
    return {
      "name": store.name,
      "tagline": store.tagline,
      "created_at": store.created_at,
      "updated_at": store.updated_at,
      "deleted_at": store.deleted_at,
      "links": [
            {"rel": "self", "href": "/store/" + store.store_id}
        ]
    }
