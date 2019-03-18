from kafka import KafkaProducer

KAKFA_SERVER = '172.20.0.6:9092'


def produce_message(document):
    """
    sends mongo changed object to kafka topic

    :param document: document being edited
    :return: Kafka Result object
    """
    producer = KafkaProducer(bootstrap_servers=KAKFA_SERVER)
    result = producer.send(document._get_collection_name(), bytes(document.to_json(), "utf-8")).get(timeout=2)
    return result