from flask import current_app


def add_to_index(document):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in document.__searchable__:
        payload[field] = getattr(document, field)
    current_app.elasticsearch.index(index=document._get_collection_name(), doc_type=document._get_collection_name()
                                    , id=document.id, body=payload)


def remove_from_index(document):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=document._get_collection_name()
                                     , doc_type=document._get_collection_name(), id=document.id)


def query_index(index, query, max, cls):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index, doc_type=index,
        body={'query': {'multi_match': {'query': query, 'fields': cls.__searchable__}},
              'from': 0, 'size': max})
    ids = [hit['_id'] for hit in search['hits']['hits']]
    return ids, search['hits']['total']