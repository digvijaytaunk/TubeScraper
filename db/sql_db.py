from globs import MY_SQL_HOST, MY_SQL_PASSWORD, MY_SQL_USER, MY_SQL_DATABASE, MY_SQL_YOUTUBER_TABLE_NAME
import mysql.connector as connection


class MySql:

    def __init__(self):
        self._connection = connection.connect(host=MY_SQL_HOST, user=MY_SQL_USER, password=MY_SQL_PASSWORD)
        self._cursor = self._connection.cursor()

    def write_to_youtuber(self, c_id: str, name: str):
        query = f'INSERT INTO {MY_SQL_DATABASE}.{MY_SQL_YOUTUBER_TABLE_NAME} ' \
                f'(`channel_id`, `channel_name`) ' \
                f'VALUES ("{c_id}", "{name}")'
        try:
            self._cursor.execute(query)
            self._connection.commit()
        except Exception as e:
            print(e)

    def read_youtuber_table(self):
        query = f'SELECT * FROM {MY_SQL_DATABASE}.{MY_SQL_YOUTUBER_TABLE_NAME}'
        self._cursor.execute(query)
        all_records = self._cursor.fetchall()
        return all_records


if __name__ == '__main__':

    channel_id = 'some id2'
    channel_name = 'some name3'

    s = MySql()
    s.write_to_youtuber(channel_id, channel_name)
    print(s.read_youtuber_table())



