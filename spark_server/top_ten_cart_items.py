from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import redis

from spark_settings import *


def main():
    sc = SparkContext(appName="top_ten_cart_items")
    ssc = StreamingContext(sc, 3)
    ssc.checkpoint(SPARK_STREAMING_CHECKPOINT_DIR)
    sc.setLogLevel("OFF")

    cart_stream = KafkaUtils.createDirectStream(ssc, [KAKFA_CART_TOPIC], {"metadata.broker.list": KAFKA_BROKER})
    carts = cart_stream.map(lambda x: (json.loads(x[1]).get("_id"), json.loads(x[1]))).window(300)

    cart_item_stream = KafkaUtils.createDirectStream(ssc, [KAFKA_CART_ITEM_TOPIC]
                                                     , {"metadata.broker.list": KAFKA_BROKER})
    cart_items = cart_item_stream.map(lambda x: (json.loads(x[1]).get("cart_id"), json.loads(x[1]))).window(60)

    customer_stream = KafkaUtils.createDirectStream(ssc, [KAFKA_CUSTOMER_TOPIC],
                                                    {"metadata.broker.list": KAFKA_BROKER})
    customers = customer_stream.map(lambda x: (json.loads(x[1]).get("_id"), json.loads(x[1]))).window(3600)

    combined = carts.join(cart_items)

    customer_and_products = combined.map(lambda x: (x[1][0].get("customer_id")
                                         , (
                                             x[1][1].get("product_id"), x[1][1].get("quantity")
                                         )
                                         ))
    combine_with_customer_stream = customer_and_products.join(customers)

    by_store = combine_with_customer_stream.map(lambda x: (x[1][0][0] + "|" + x[1][1].get("store_id"), x[1][0]))

    def update_function(new_values, running_count):
        if running_count is None:
            running_count = 0
        try:
            return int(new_values[1][1]) + running_count
        except IndexError:
            return running_count

    def send_updated_results_to_redis(rdd):
        response_count_json = json.dumps(rdd.collectAsMap())
        redis_conn = get_redis_connection()
        redis_conn.set('Store_Product_Count', response_count_json)

    store_product_count = by_store.updateStateByKey(update_function)
    store_product_count.foreachRDD(send_updated_results_to_redis)

    ssc.start()
    ssc.awaitTermination()


def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


if __name__ == "__main__":
    main()