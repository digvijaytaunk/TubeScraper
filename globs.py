import os
from enum import Enum

API_KEY = os.getenv('GCP_TUBESCRAPER_API_KEY')
DB_PORT = 3306

MY_SQL_USER = os.getenv('AWS_MYSQL_MASTER_USER')
MY_SQL_PASSWORD = os.getenv('AWS_MYSQL_MASTER_PASSWORD')
MY_SQL_HOST = os.getenv('AWS_MYSQL_HOST')

MY_SQL_DATABASE = 'tubescraper'
MY_SQL_YOUTUBER_TABLE_NAME = 'youtuber'
MY_SQL_VIDEOS_TABLE_NAME = 'videos'


MONGO_USER = os.getenv('MONGO_DB_CLOUD_USER')
MONGO_PASSWORD = os.getenv('MONGO_DB_CLOUD_PASSWORD')
MONGO_DB_NAME = 'tubescraper_db'
MONGO_DB_COLLECTION_NAME = 'comments_collection'
MONGO_CONNECTION_STRING = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.malrj.mongodb.net/?retryWrites=true&w=majority"


class STATUS(Enum):
    FAIL = 'fail'
    SUCCESS = 'success'
