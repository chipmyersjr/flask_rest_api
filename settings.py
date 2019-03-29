import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True
MONGODB_HOST = "172.20.0.7"
MONGODB_DB = "store"
ELASTICSEARCH_URL = "172.20.0.8:9200"
MAIL_SERVER = "smtp.mailgun.org"
MAIL_PORT = 25
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_USE_TLS = False
MAIL_USE_SSL = False