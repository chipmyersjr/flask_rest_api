from flask import jsonify


def paginated_results(objects, collection_name, request, per_page, serialization_func):
    """
    returns standard paginated results response for get methods

    :param objects: mongo queryset object to be paginated
    :param collection_name: mongo collecion name
    :param request: request object from flask to get page
    :param per_page: number of results per page
    :param serialization_func: function for serializing the mongo actions
    :return: json repsonse
    """
    href = "/" + collection_name + "/?page=%s"

    page = int(request.args.get('page', 1))
    paginated_objects = objects.paginate(page=page, per_page=per_page)

    response = {
        "result": "ok",
        "links": [
            {
                "href": href % page,
                "rel": "self"
            }
        ],
        collection_name + "s": serialization_func(paginated_objects)
    }
    if paginated_objects.has_prev:
        response["links"].append(
            {
                "href": href % paginated_objects.prev_num,
                "rel": "previous"
            }
        )
    if paginated_objects.has_next:
        response["links"].append(
            {
                "href": href % paginated_objects.next_num,
                "rel": "next"
            }
        )
    return jsonify(response)
