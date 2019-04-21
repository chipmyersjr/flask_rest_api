from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import redis

KAKFA_CART_TOPIC = "cart"
KAFKA_CART_ITEM_TOPIC = "cart_item"
KAFKA_CUSTOMER_TOPIC = "customer"
KAFKA_BROKER = "172.20.0.6:9092"
SPARK_STREAMING_CHECKPOINT_DIR = "/home/data"
REDIS_HOST = "172.20.0.4"
REDIS_PORT = "6379"


def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


r = get_redis_connection()

print(r.get("Top_Coupon_Code"))

