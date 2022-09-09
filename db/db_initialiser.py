from globs import MY_SQL_DATABASE, MY_SQL_VIDEOS_TABLE_NAME, MY_SQL_YOUTUBER_TABLE_NAME

create_database = f'CREATE DATABASE {MY_SQL_DATABASE}'

videos_create_table_query = f'CREATE TABLE `{MY_SQL_DATABASE}`.`{MY_SQL_VIDEOS_TABLE_NAME}` (' \
                            '  `index` INT NOT NULL AUTO_INCREMENT,' \
                            '  `channel_id` VARCHAR(45) NOT NULL,' \
                            '  `video_id` VARCHAR(45) NOT NULL,' \
                            '  `title` VARCHAR(200) NOT NULL,' \
                            '  `youtube_link` VARCHAR(200) NOT NULL,' \
                            '  `s3_link` VARCHAR(200) NULL,' \
                            '  `likes` INT NULL,' \
                            '  `comments_count` INT NULL,' \
                            '  `views` INT NULL,' \
                            '  `thumbnail_link` VARCHAR(200) NULL,' \
                            '  PRIMARY KEY (`index`),' \
                            '  UNIQUE INDEX `video_id_UNIQUE` (`video_id` ASC) VISIBLE);'


youtuber_create_table_query = f'CREATE TABLE `{MY_SQL_DATABASE}`.`{MY_SQL_YOUTUBER_TABLE_NAME}` (' \
                              '`channel_id` VARCHAR(45) NOT NULL,' \
                              '`channel_name` VARCHAR(45) NOT NULL,' \
                              'PRIMARY KEY (`channel_id`),' \
                              'UNIQUE INDEX `channel_id_UNIQUE` (`channel_id` ASC) VISIBLE)'
