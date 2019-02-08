def store_obj(store):
    return {
      "store_id": store.store_id,
      "name": store.name,
      "tagline": store.tagline,
      "credit_order_preference": store.credit_order_preference,
      "created_at": store.created_at,
      "updated_at": store.updated_at,
      "deleted_at": store.deleted_at
    }
