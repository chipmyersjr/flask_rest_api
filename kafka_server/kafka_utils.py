from kafka import KafkaProducer
import boto3

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


def produce_kinesis_message(document):
    """
    sends mongo changed object to kinesis stream

    :param document: document being edited
    :return: Kinesis Result object
    """
    stream_name = 'flask_app_customer_collection'
    kinesis_client = boto3.client('kinesis', region_name='us-west-2')

    result = kinesis_client.put_record(StreamName=stream_name,
                                       Data=document.to_json(),
                                       PartitionKey="_id")

    return result