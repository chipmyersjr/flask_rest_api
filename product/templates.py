def product_obj(product):
    return {
      "product_id": product.id,
      "title": product.title,
      "product_type": product.product_type,
      "vendor": product.vendor,
      "created_at": product.created_at,
      "updated_at": product.updated_at,
      "deleted_at": product.deleted_at
    }


def products_obj(products):
    products_obj_list = []
    for product in products.items:
        products_obj_list.append(product_obj(product))
    return products_obj_list
