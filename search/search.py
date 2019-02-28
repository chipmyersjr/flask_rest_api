from flask import current_app


def add_to_index(index, model, _id):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, doc_type=index, id=_id, body=payload)


def remove_from_index(index, id):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, doc_type=index, id=id)


def query_index(index, query, num_items):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index, doc_type=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['test']}},
              'from': 0, 'size': num_items})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']