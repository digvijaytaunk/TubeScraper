from typing import Dict, List, Tuple

from db.db_initialiser import youtuber_create_table_query, videos_create_table_query
from globs import MY_SQL_HOST, MY_SQL_PASSWORD, MY_SQL_USER, MY_SQL_DATABASE, MY_SQL_YOUTUBER_TABLE_NAME, STATUS, \
    MY_SQL_VIDEOS_TABLE_NAME
import mysql.connector as connection

from scaper.video import Video


class MySql:

    def __init__(self, logger):
        self.LOGGER = logger

    def _get_connection(self):
        try:
            obj = connection.connect(host=MY_SQL_HOST, user=MY_SQL_USER, password=MY_SQL_PASSWORD)
            return obj
        except:
            return None

    def get_cursor(self):
        if not self._get_connection():
            return None
        return self._get_connection().cursor()

    def save_videos(self, all_videos: List[Video]) -> Dict:
        """
        Saves the passed video to database if does not exists already
        :param all_videos: LIst[Video]: List if Video object
        :return: Dict{videoId: status}: Video Id as a key, status of video = saved or exist
        """
        self.LOGGER.info(f'Initiated Saving videos to MySQL.')
        channel_id = all_videos[0].channel_id

        saved_video_list = self._get_saved_video_id(channel_id)

        all_video_id = [video.videoId for video in all_videos]
        new_ids = [v_id for v_id in all_video_id if v_id not in saved_video_list]
        new_videos = [video for video in all_videos if video.videoId in new_ids]

        try:
            if len(new_videos) > 0:
                self._write_to_videos(new_videos)
            self.LOGGER.warning('All the latest videos already saved in database.')
        except Exception as e:
            self.LOGGER.error(f'Failed to write to SQl DB. {e}')
            return {'status': STATUS.FAIL}

        self.LOGGER.info('Writing to SQl DB success.')
        return {'status': STATUS.SUCCESS}

    def _get_saved_video_id(self, channel_id: str) -> List[str]:
        """
        Returns the list of id of the videos saved in database of the provided channel ID
        :param channel_id: str
        :return: List[str]: List of youtube video id
        """
        query = f'SELECT `video_id` FROM {MY_SQL_DATABASE}.{MY_SQL_VIDEOS_TABLE_NAME} WHERE `channel_id`="{channel_id}"'
        self.LOGGER.info(f'Fetching saved video with SQl query {query}.')
        cursor = self.get_cursor()
        cursor.execute(query)
        res = cursor.fetchall()
        saved_id = []
        for item in res:
            saved_id.append(item[0])

        self.LOGGER.debug(f'Found saved video from SQL DB {saved_id}.')
        return saved_id

    def save_youtuber_data(self, video_obj: Video) -> Dict:
        """
        Adds a new record in in youtuber database if does not exists.
        :param video_obj: Video: Video object with channel_id populated
        :return: Dict{status}: Dictionary with status flag
        """

        channel_id = video_obj.channel_id
        channel_name = video_obj.channel_name
        self.LOGGER.info(f'Saving youtuber data to SQl DB - {channel_name}.')
        if self._is_channel_exists(channel_id):
            self.LOGGER.warning(f'Youtuber data exists in SQl DB for ID {channel_name}.')
            return {'status': STATUS.FAIL}

        status = self._write_to_youtuber(channel_id, channel_name)

        self.LOGGER.info(f'Youtuber data saved to SQL DB STATUS {status["status"]}.')
        return {'status': STATUS.SUCCESS} if status['status'] == STATUS.SUCCESS else {'status': STATUS.FAIL}

    def update_s3_address(self, video_list: List[Video]):
        for video in video_list:
            if video.s3_url != '':
                self._update_s3_address(video)

    def _update_s3_address(self, video: Video) -> bool:
        query = f'UPDATE {MY_SQL_DATABASE}.{MY_SQL_VIDEOS_TABLE_NAME} SET `s3_link` = "{video.s3_url}" WHERE `video_id` = "{video.videoId}"'
        try:
            self.LOGGER.info(f'Updating S3 url for video ID - {video.videoId}')
            self._cursor.execute(query)
            self._connection.commit()
        except Exception as e:
            self.LOGGER.error(f'Failed to update S3 url for video ID {video.videoId}. {e}.')
            return False

        return True

    def _is_channel_exists(self, channel_id: str) -> bool:
        """
        Checks if the channel id exists in youtuber database table
        :param channel_id:
        :return:
        """
        query = f'SELECT * FROM {MY_SQL_DATABASE}.{MY_SQL_YOUTUBER_TABLE_NAME} WHERE `channel_id`="{channel_id}"'
        self._cursor.execute(query)
        all_records = self._cursor.fetchall()
        return len(all_records) == 1

    def read_youtuber_table(self):
        query = f'SELECT * FROM {MY_SQL_DATABASE}.{MY_SQL_YOUTUBER_TABLE_NAME}'
        self.LOGGER.info(f'Reading youtuber data from SQl DB query - {query}.')
        self._cursor.execute(query)
        all_records = self._cursor.fetchall()
        self.LOGGER.info(f'Found youtuber data from SQl DB - {all_records}.')
        return all_records

    def _write_to_youtuber(self, c_id: str, name: str) -> Dict:
        query = f'INSERT INTO {MY_SQL_DATABASE}.{MY_SQL_YOUTUBER_TABLE_NAME} ' \
                f'(`channel_id`, `channel_name`) ' \
                f'VALUES ("{c_id}", "{name}")'
        try:
            self.LOGGER.info(f'Writing youtuber data to SQl DB query - {query}.')
            self._cursor.execute(query)
            self._connection.commit()
        except Exception as e:
            self.LOGGER.eror(f'Failed to write youtuber data from SQl DB query - {query}. {e}')
            return {'status': STATUS.FAIL}

        return {'status': STATUS.SUCCESS}

    def _write_to_videos(self, video_list: List[Video]) -> bool:
        self.LOGGER.info(f'Initialised writing video data to SQl DB.')
        value_params = []
        for video in video_list:
            value_params.append(f'("{video.channel_id}", "{video.videoId}", "{video.title}", "{video.watch_url}", "", "{video.likes}", "{video.comment_count}", "{video.views}","{video.thumbnail_url}")')

        values = ', '.join(value_params)
        query = f'INSERT INTO {MY_SQL_DATABASE}.{MY_SQL_VIDEOS_TABLE_NAME} ' \
                f'(`channel_id`,`video_id`, `title`, `youtube_link`, `s3_link`, `likes`, `comments_count`, `views`, `thumbnail_link`) ' \
                f'VALUES {values}'
        try:
            self.LOGGER.info(f'Writing video data to SQl DB query - {query}.')
            self._cursor.execute(query)
            self._connection.commit()
        except Exception as e:
            self.LOGGER.error(f'Failed to write video data to SQl DB - {e}.')
            return False

        return True

    # for maintenance only
    def reset_tables(self):
        try:
            q = f'USE {MY_SQL_DATABASE}'
            self._cursor.execute(q)

            q = f'DROP TABLE {MY_SQL_YOUTUBER_TABLE_NAME}'
            self._cursor.execute(q)

            self._cursor.execute(youtuber_create_table_query)

            q = f'DROP TABLE {MY_SQL_VIDEOS_TABLE_NAME}'
            self._cursor.execute(q)

            self._cursor.execute(videos_create_table_query)
            self.LOGGER.info(f'Reset SQL table success.')
        except Exception as e:
            self.LOGGER.error(f'Failed to reset SQL table. {e}')


if __name__ == '__main__':
    ch_id = 'some id2'
    ch_name = 'some name3'

    s = MySql()
    # s._write_to_youtuber(ch_id, ch_name)
    # print(s.read_youtuber_table())

    # data = s._is_channel_exists(ch_id)
    # print(data)

    v1 = Video(
        channel_id='UCR5e82h9PJ6dxsO6rBQuxlg',
        channel_name='channel_name',
        published_at='published_at',
        video_id='video_id1',
        title='title',
        thumbnail_url='thumbnail_url',
        likes='likes',
        views='views',
        comment_count='comment_count',
        watch_url='watch_url',
        comment_thread='comment_thread'
    )
    v2 = Video(
        channel_id='UCR5e82h9PJ6dxsO6rBQuxlg',
        channel_name='channel_name',
        published_at='published_at',
        video_id='video_id2',
        title='title',
        thumbnail_url='thumbnail_url',
        likes='likes',
        views='views',
        comment_count='comment_count',
        watch_url='watch_url',
        comment_thread='comment_thread'
    )
    l = [v1, v2]
    print(s._write_to_videos(l))
