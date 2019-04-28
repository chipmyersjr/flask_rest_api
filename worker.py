import os

import redis
from rq import Worker, Queue, Connection

REDIS_HOST = "172.20.0.4"
REDIS_PORT = "6379"

listen = ['default']

conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()