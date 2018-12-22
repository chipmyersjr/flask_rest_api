def product_obj(product):
    return {
      "id": product.id,
      "title": product.title,
      "product_type": product.product_type,
      "vendor": product.vendor,
      "created_at": product.created_at,
      "updated_at": product.updated_at
    }
