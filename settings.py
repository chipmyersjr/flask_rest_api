import os

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True
MONGODB_HOST = "mongodb"
MONGODB_DB = os.getenv("MONGODB_DB")
ELASTICSEARCH_URL = "elasticsearch:9200"