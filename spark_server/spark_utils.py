import redis
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SparkSession
import json

KAFKA_INVOICE_TOPIC = "invoice"
KAFKA_CUSTOMER_TOPIC = "customer"
KAFKA_INVOICE_LINE_ITEM_TOPIC = "invoice_line_item"
KAFKA_BROKER = "172.20.0.6:9092"
SPARK_STREAMING_CHECKPOINT_DIR = "/home/data"
REDIS_HOST = "172.20.0.4"
REDIS_PORT = "6379"
KAKFA_CART_TOPIC = "cart"
KAFKA_CART_ITEM_TOPIC = "cart_item"
KAFKA_COUPON_CODE_REDEMPTION = "coupon_code_redemption"
KAFKA_COUPON_CODE_TOPIC = "coupon_code"


def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def get_spark_session_instance():
    if 'sparkSessionSingletonInstance' not in globals():
        globals()['sparkSessionSingletonInstance'] = SparkSession\
            .builder\
            .getOrCreate()
    return globals()['sparkSessionSingletonInstance']


def get_distinct_customers(streaming_context, window=3600):
    customer_stream = KafkaUtils.createDirectStream(streaming_context, [KAFKA_CUSTOMER_TOPIC],
                                                    {"metadata.broker.list": KAFKA_BROKER})
    customers = customer_stream.map(lambda x: (json.loads(x[1]).get("_id"), json.loads(x[1]).get("store_id"))) \
        .window(window)

    return customers.transform(lambda x: x.distinct())


