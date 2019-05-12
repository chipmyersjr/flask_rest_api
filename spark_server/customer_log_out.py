from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from datetime import datetime

from spark_utils import *


def main():
    sc = SparkContext(appName="customer_logins")
    ssc = StreamingContext(sc, 3)
    ssc.checkpoint(SPARK_STREAMING_CHECKPOINT_DIR)
    sc.setLogLevel("OFF")

    distinct_customers = get_distinct_customers(ssc).map(lambda x: (x[1], 1))

    result = distinct_customers.reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y: x - y, 85998, 3)

    def send_updated_results_to_redis(rdd):
        response_count_json = rdd.collectAsMap()
        redis_conn = get_redis_connection()
        redis_conn.set('Customer_Logins', json.dumps(response_count_json))

    result.pprint()
    result.foreachRDD(send_updated_results_to_redis)

    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    main()