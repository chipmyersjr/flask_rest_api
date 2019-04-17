from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import redis

from spark_settings import *


def main():
    sc = SparkContext(appName="invoice_amount")
    ssc = StreamingContext(sc, 3)
    ssc.checkpoint(SPARK_STREAMING_CHECKPOINT_DIR)
    sc.setLogLevel("OFF")

    invoice_stream = KafkaUtils.createDirectStream(ssc, [KAFKA_INVOICE_TOPIC], {"metadata.broker.list": KAFKA_BROKER})
    invoices = invoice_stream.map(lambda x: (json.loads(x[1]).get("_id"), json.loads(x[1]).get("customer_id")))\
                             .window(15)

    customer_stream = KafkaUtils.createDirectStream(ssc, [KAFKA_CUSTOMER_TOPIC],
                                                    {"metadata.broker.list": KAFKA_BROKER})
    customers = customer_stream.map(lambda x: (json.loads(x[1]).get("_id"), json.loads(x[1]).get("store_id")))\
                               .window(3600)

    distinct_customers = customers.transform(lambda x: x.distinct())

    invoice_line_item_stream = KafkaUtils.createDirectStream(ssc, [KAFKA_INVOICE_LINE_ITEM_TOPIC],
                                                             {"metadata.broker.list": KAFKA_BROKER})

    invoice_line_items = invoice_line_item_stream.map(lambda x: (json.loads(x[1]).get("invoice_id")
                                                                 , float(json.loads(x[1]).get("total_amount_in_cents")
                                                                         / 100)))
    by_store = invoice_line_items.join(invoices)\
                                 .map(lambda x: (x[1][1], x[1][0]))\
                                 .join(distinct_customers)\
                                 .map(lambda x: (x[1][1], x[1][0]))

    invoice_amount = by_store.reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y: x - y, 7200, 3)

    invoice_amount.pprint()

    def send_updated_results_to_redis(rdd):
        result_count_json = json.dumps(rdd.collectAsMap())
        redis_conn = get_redis_connection()
        redis_conn.set('Invoice_Amount', result_count_json)

    invoice_amount.foreachRDD(send_updated_results_to_redis)

    ssc.start()
    ssc.awaitTermination()


def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


if __name__ == "__main__":
    main()