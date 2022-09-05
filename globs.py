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

S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')

MONGO_DB_NAME = 'tubescraper_db'
MONGO_DB_COLLECTION_NAME = 'comments_collection'

MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING')


class STATUS(Enum):
    FAIL = 'fail'
    SUCCESS = 'success'
