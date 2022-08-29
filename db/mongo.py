import os
import pymongo

mongo_user = os.getenv('MONGO_DB_CLOUD_USER')
mongo_password = os.getenv('MONGO_DB_CLOUD_PASSWORD')

client = pymongo.MongoClient(
    f"mongodb+srv://{mongo_user}:{mongo_password}@cluster0.malrj.mongodb.net/?retryWrites=true&w=majority"
)
db = client.test
mongo_database = client['ml_db']
collection = mongo_database['api_db']
