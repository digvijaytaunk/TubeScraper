from typing import Dict, List, Tuple

from globs import MY_SQL_HOST, MY_SQL_PASSWORD, MY_SQL_USER, MY_SQL_DATABASE, MY_SQL_YOUTUBER_TABLE_NAME, STATUS
import mysql.connector as connection

from scaper.video import Video


class MySql:

    def __init__(self):
        self._connection = connection.connect(host=MY_SQL_HOST, user=MY_SQL_USER, password=MY_SQL_PASSWORD)
        self._cursor = self._connection.cursor()

    def _write_to_youtuber(self, c_id: str, c_uuid: str, name: str) -> Dict:
        query = f'INSERT INTO {MY_SQL_DATABASE}.{MY_SQL_YOUTUBER_TABLE_NAME} ' \
                f'(`channel_id`, `channel_uuid`, `channel_name`) ' \
                f'VALUES ("{c_id}", "{c_uuid}", "{name}")'
        try:
            self._cursor.execute(query)
            self._connection.commit()
        except Exception as e:
            print(e)
            return {'status': STATUS.FAIL}

        return {'status': STATUS.SUCCESS}

    def save_youtuber_data(self, video_obj: Video) -> Dict:
        """
        Adds a new record in in youtuber database if does not exists.
        :param video_obj: Video: Video object with channel_id populated
        :return: Dict{status}: Dictionary with status flag
        """
        channel_id = video_obj.channel_id
        channel_uuid = video_obj.channel_uuid
        channel_name = video_obj.channel_name
        if self._is_channel_exists(channel_id):
            return {'status': STATUS.FAIL}

        status = self._write_to_youtuber(channel_id, channel_uuid, channel_name)
        return {'status': STATUS.SUCCESS} if status['status'] == STATUS.SUCCESS else {'status': STATUS.FAIL}

    def _is_channel_exists(self, channel_id: str) -> bool:
        """
        Checks if the channel id exists in youtuber database table
        :param channel_id:
        :return:
        """
        query = f'SELECT * FROM {MY_SQL_DATABASE}.{MY_SQL_YOUTUBER_TABLE_NAME} WHERE `channel_id`="{channel_id}"'
        res = self._run_read_query(query)
        return len(res) == 1

    def read_youtuber_table(self):
        query = f'SELECT * FROM {MY_SQL_DATABASE}.{MY_SQL_YOUTUBER_TABLE_NAME}'
        self._cursor.execute(query)
        all_records = self._cursor.fetchall()
        return all_records

    def _run_read_query(self, query):
        self._cursor.execute(query)
        all_records = self._cursor.fetchall()
        return all_records


if __name__ == '__main__':

    ch_id = 'some id2'
    ch_name = 'some name3'

    s = MySql()
    # s._write_to_youtuber(ch_id, ch_name)
    # print(s.read_youtuber_table())

    data = s._is_channel_exists(ch_id)
    print(data)


