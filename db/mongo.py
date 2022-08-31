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

# DB schema for mongo
record = {
    'video_id'  # id from sql video table
    'comments': [
        {
            'comment_auther'
            'message'
        }

    ]
}


# Dict for python to store extracted data
data = {
    'channel_id'
    'channel_name'
    'videos': [
        {
            'title'
            'url'  # video link
            'likes'
            'comments_count'
            'thumbnail_link'
            's3_link'  # Added after the file is uploaded to S3 bucket
        }
    ]
}
