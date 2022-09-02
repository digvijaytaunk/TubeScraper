import os
from typing import List

import pymongo

from globs import MONGO_USER, MONGO_PASSWORD, MONGO_DB_NAME, MONGO_DB_COLLECTION_NAME
from scaper.video import Video


class MongoDb:
    def __init__(self):
        self._client = pymongo.MongoClient(
            f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.malrj.mongodb.net/?retryWrites=true&w=majority")

        self._database_name = self._client[MONGO_DB_NAME]
        self._collection = self._database_name[MONGO_DB_COLLECTION_NAME]

    def save_comments(self, videos: List[Video]):
        data_list = []
        for video in videos:
            data = {
                'video_id': video.videoId,
                'comments': video.comment_thread
            }
            data_list.append(data)

        try:
            self._collection.insert_many(data_list)
        except Exception as e:
            print(e)
            return False

        return True






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
