from mongoengine import signals

from utils import handler
from search.search import add_to_index, remove_from_index


@handler(signals.post_save)
def search_reindex(sender, document, created):
    add_to_index(document)

    if document.deleted_at is not None:
        remove_from_index(document=document)