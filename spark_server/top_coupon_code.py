from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import Row
import json
import redis
from collections import OrderedDict

from spark_utils import *


def main():
    sc = SparkContext(appName="top_coupon_code")
    ssc = StreamingContext(sc, 3)
    ssc.checkpoint(SPARK_STREAMING_CHECKPOINT_DIR)
    sc.setLogLevel("OFF")

    redemption_stream = KafkaUtils.createDirectStream(ssc, [KAFKA_COUPON_CODE_REDEMPTION]
                                                      , {"metadata.broker.list": KAFKA_BROKER})
    redemptions = redemption_stream.map(lambda x: (json.loads(x[1]).get("coupon_code_id"), 1))

    by_coupon_sum = redemptions.reduceByKeyAndWindow(lambda x, y: x + y, lambda x, y: x - y, 7200, 3)

    coupon_code_stream = KafkaUtils.createDirectStream(ssc, [KAFKA_COUPON_CODE_TOPIC]
                                                       , {"metadata.broker.list": KAFKA_BROKER})
    coupon_codes = coupon_code_stream.map(lambda x: (json.loads(x[1]).get("_id"), json.loads(x[1]).get("store_id")))\
                                     .window(7200)

    distinct_coupons = coupon_codes.transform(lambda x: x.distinct())

    result = by_coupon_sum.join(distinct_coupons).map(lambda x: (x[0], [x[1][1], x[1][0]]))

    def send_updated_results_to_redis(rdd):
        response_count_json = rdd.collectAsMap()
        redis_conn = get_redis_connection()
        redis_conn.set('Top_Coupon_Code', json.dumps(response_count_json))

    result.pprint()
    result.foreachRDD(send_updated_results_to_redis)

    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    main()