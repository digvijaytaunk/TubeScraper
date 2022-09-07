from typing import Dict, List, Tuple

from db.db_initialiser import youtuber_create_table_query, videos_create_table_query
from globs import MY_SQL_HOST, MY_SQL_PASSWORD, MY_SQL_USER, MY_SQL_DATABASE, MY_SQL_YOUTUBER_TABLE_NAME, STATUS, \
    MY_SQL_VIDEOS_TABLE_NAME
import mysql.connector as connection

from scaper.video import Video


class MySql:

    def __init__(self, logger):
        self._connection = connection.connect(host=MY_SQL_HOST, user=MY_SQL_USER, password=MY_SQL_PASSWORD)
        self._cursor = self._connection.cursor()
        self.LOGGER = logger

    def save_videos(self, all_videos: List[Video]) -> bool:
        """
        Saves the passed video to database if does not exists already
        :param all_videos: LIst[Video]: List if Video object
        :return: Dict{videoId: status}: Video Id as a key, status of video = saved or exist
        """
        channel_id = all_videos[0].channel_id

        saved_video_list = self._get_saved_video_id(channel_id)

        all_video_id = [video.videoId for video in all_videos]
        new_ids = [v_id for v_id in all_video_id if v_id not in saved_video_list]
        new_videos = [video for video in all_videos if video.videoId in new_ids]

        try:
            self.LOGGER.debug('This is a DEBUG log record FROM MySql MySql MySql MySql MySql save_videos.')
            self._write_to_videos(new_videos)
        except Exception as e:
            print(e)
            return False

        return True

    def _get_saved_video_id(self, channel_id: str) -> List[str]:
        """
        Returns the list of id of the videos saved in database of the provided channel ID
        :param channel_id: str
        :return: List[str]: List of youtube video id
        """
        query = f'SELECT `video_id` FROM {MY_SQL_DATABASE}.{MY_SQL_VIDEOS_TABLE_NAME} WHERE `channel_id`="{channel_id}"'
        self._cursor.execute(query)
        res = self._cursor.fetchall()
        saved_id = []
        for item in res:
            saved_id.append(item[0])

        self.LOGGER.debug('This is a DEBUG log record FROM MySql MySql MySql MySql MySql _get_saved_video_id.')
        return saved_id

    def save_youtuber_data(self, video_obj: Video) -> Dict:
        """
        Adds a new record in in youtuber database if does not exists.
        :param video_obj: Video: Video object with channel_id populated
        :return: Dict{status}: Dictionary with status flag
        """
        channel_id = video_obj.channel_id
        channel_name = video_obj.channel_name
        if self._is_channel_exists(channel_id):
            return {'status': STATUS.FAIL}

        self.LOGGER.debug('This is a DEBUG log record FROM MySql MySql MySql MySql MySql save_youtuber_data.')
        status = self._write_to_youtuber(channel_id, channel_name)
        return {'status': STATUS.SUCCESS} if status['status'] == STATUS.SUCCESS else {'status': STATUS.FAIL}

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
        self._cursor.execute(query)
        all_records = self._cursor.fetchall()
        return all_records

    def _write_to_youtuber(self, c_id: str, name: str) -> Dict:
        query = f'INSERT INTO {MY_SQL_DATABASE}.{MY_SQL_YOUTUBER_TABLE_NAME} ' \
                f'(`channel_id`, `channel_name`) ' \
                f'VALUES ("{c_id}", "{name}")'
        try:
            self._cursor.execute(query)
            self._connection.commit()
        except Exception as e:
            print(e)
            return {'status': STATUS.FAIL}

        return {'status': STATUS.SUCCESS}

    def _write_to_videos(self, video_list: List[Video]) -> bool:
        value_params = []
        for video in video_list:
            value_params.append(f'("{video.channel_id}", "{video.videoId}", "{video.title}", "{video.watch_url}", "s3_link", "{video.likes}", "{video.comment_count}", "{video.views}","{video.thumbnail_url}")')

        values = ', '.join(value_params)
        query = f'INSERT INTO {MY_SQL_DATABASE}.{MY_SQL_VIDEOS_TABLE_NAME} ' \
                f'(`channel_id`,`video_id`, `title`, `youtube_link`, `s3_link`, `likes`, `comments_count`, `views`, `thumbnail_link`) ' \
                f'VALUES {values}'
        try:
            self._cursor.execute(query)
            self._connection.commit()
        except Exception as e:
            print(e)
            return False

        return True

    # for maintenance only
    def reset_tables(self):
        try:
            q = f'USE {MY_SQL_DATABASE}'
            self._cursor.execute(q)

            q = f'DROP TABLE {MY_SQL_YOUTUBER_TABLE_NAME}'
            self._cursor.execute(q)

            q = youtuber_create_table_query
            self._cursor.execute(q)

            q = f'DROP TABLE {MY_SQL_VIDEOS_TABLE_NAME}'
            self._cursor.execute(q)

            q = videos_create_table_query
            self._cursor.execute(q)

        except Exception:
            pass



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
