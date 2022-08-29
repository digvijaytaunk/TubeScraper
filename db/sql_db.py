import os
import mysql.connector as connection

user_name = os.getenv('MYSQL_DB_LOCAL_USER')
password = os.getenv('MYSQL_DB_LOCAL_PASSWORD')

host = "localhost"
database = 'ineuron'
table = 'api_db'

conn = connection.connect(host=host, user=user_name, password=password)
cursor = conn.cursor()
