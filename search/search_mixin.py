from search.search import query_index


class SearchableMixin:

    def __init__(self):
        pass

    @classmethod
    def search(cls, expression, max):
        ids, total = query_index(cls._get_collection_name(), expression, max, cls)
        if total == 0:
            return None
        return cls.objects.filter(product_id__in=ids).all()