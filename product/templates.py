def product_obj(product):
    return {
      "product_id": product.id,
      "title": product.title,
      "product_type": product.product_type,
      "description": product.description,
      "vendor": product.vendor,
      "inventory": product.inventory,
      "sale_price_in_cents": product.sale_price_in_cents,
      "tags": tag_objs(product.get_tags()),
      "created_at": product.created_at,
      "updated_at": product.updated_at,
      "deleted_at": product.deleted_at,
      "links": [
            {"rel": "self", "href": "/product/" + product.id}
        ]
    }


def products_obj(products):
    products_obj_list = []
    for product in products.items:
        products_obj_list.append(product_obj(product))
    return products_obj_list


def tag_obj(tag):
    return {
        "email_id": tag.product_tag_id,
        "tag": tag.tag,
        "created_at": tag.created_at,
        "deleted_at": tag.deleted_at
    }


def tag_objs(tags):
    obj_list = []
    for tag in tags:
        obj_list.append(tag_obj(tag))
    return obj_list