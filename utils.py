from flask import jsonify
import redis

REDIS_HOST = "172.20.0.4"
REDIS_PORT = "6379"


def paginated_results(objects, collection_name, request, per_page, serialization_func, dictionary=False):
    """
    returns standard paginated results response for get methods

    :param objects: mongo queryset object to be paginated
    :param collection_name: mongo collecion name
    :param request: request object from flask to get page
    :param per_page: number of results per page
    :param serialization_func: function for serializing the mongo actions
    :param dictionary: if true returns a dictionary instead of a response object
    :return: json repsonse
    """
    href = "/" + collection_name + "/?page=%s"

    page = int(request.args.get('page', 1))
    paginated_objects = objects.paginate(page=page, per_page=per_page)

    plural = collection_name + "es" if collection_name[-1] == "s" else collection_name + "s"
    response = {
        "result": "ok",
        "links": [
            {
                "href": href % page,
                "rel": "self"
            }
        ],
        plural: serialization_func(paginated_objects)
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

    if dictionary:
        return response

    return jsonify(response)


def handler(event):
    """Signal decorator to allow use of callback functions as class decorators."""

    def decorator(fn):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls

        fn.apply = apply
        return fn

    return decorator


def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


class DuplicateDataError(Exception):
    pass
