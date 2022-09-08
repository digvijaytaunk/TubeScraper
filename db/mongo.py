from typing import List

import pymongo

from globs import MONGO_DB_NAME, MONGO_DB_COLLECTION_NAME, MONGO_CONNECTION_STRING
from scaper.video import Video


class MongoDb:
    def __init__(self, logger):
        self._client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
        self.LOGGER = logger
        self._database_name = self._client[MONGO_DB_NAME]
        self._collection = self._database_name[MONGO_DB_COLLECTION_NAME]

    def save_comments(self, videos: List[Video]):
        self.LOGGER.info(f'Initiated saving comments to Mongo.')
        data_list = []
        for video in videos:
            data = {
                'video_id': video.videoId,
                'thumbnail_base64': video.thumbnail_base64,
                'comments': video.comment_thread
            }
            data_list.append(data)

        try:
            self.LOGGER.info(f'Saving comment {data_list}.')
            self._collection.insert_many(data_list)
        except Exception as e:
            self.LOGGER.error(f'Failed to save comments. {e}.')
            return False

        return True

    def reset_collection(self):
        self._collection.drop()
        self._database_name.create_collection(MONGO_DB_COLLECTION_NAME)
        self.LOGGER.info(f'Reset MongoDB done.')

