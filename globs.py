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


class STATUS(Enum):
    FAIL = 'fail'
    SUCCESS = 'success'
