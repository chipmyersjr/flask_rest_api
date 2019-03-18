from mongoengine import signals

from utils import handler
from kafka_server.kafka_utils import produce_message


@handler(signals.post_save)
def produces_kafka_message(sender, document, created):
    produce_message(document)