from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from datetime import datetime

from spark_utils import *


def main():
    sc = SparkContext(appName="new_customers")
    ssc = StreamingContext(sc, 3)
    ssc.checkpoint(SPARK_STREAMING_CHECKPOINT_DIR)
    sc.setLogLevel("OFF")

    customer_stream = KafkaUtils.createDirectStream(ssc, [KAFKA_CUSTOMER_TOPIC],
                                                    {"metadata.broker.list": KAFKA_BROKER})
    customers = customer_stream.map(lambda x: (json.loads(x[1]).get("store_id")
                                               , (json.loads(x[1]).get("_id")
                                                  , json.loads(x[1]).get("created_at")["$date"]))) \
        .window(85998)

    def filter_created_today(customer):
        dt = datetime.fromtimestamp(customer[1][1])
        difference = datetime.now() - dt

        return difference.days == 0

    customers.filter(filter_created_today)

    distinct_customers = customers.transform(lambda x: x.distinct()).map(lambda x: (x[0], 1))

    result = distinct_customers.reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y: x - y, 85998, 3)

    def send_updated_results_to_redis(rdd):
        response_count_json = rdd.collectAsMap()
        redis_conn = get_redis_connection()
        redis_conn.set('New_Customers', json.dumps(response_count_json))

    result.pprint()
    result.foreachRDD(send_updated_results_to_redis)

    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    main()