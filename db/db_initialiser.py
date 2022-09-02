create_database = 'CREATE DATABASE ineuron'

youtuber_table_query = 'CREATE TABLE `tubescraper`.`youtuber` (' \
                       '`index` INT NOT NULL AUTO_INCREMENT,' \
                       ' `channel_id` VARCHAR(45) NOT NULL,' \
                       ' `channel_name` VARCHAR(45) NOT NULL,' \
                       '  PRIMARY KEY (`uuid`),' \
                       '  UNIQUE INDEX `uuid_UNIQUE` (`uuid` ASC) VISIBLE,' \
                       '  UNIQUE INDEX `index_UNIQUE` (`index` ASC) VISIBLE);'

videos_table_query = 'CREATE TABLE `sys`.`videos` (' \
                     '`index` INT NOT NULL AUTO_INCREMENT, ' \
                     '`channel_id` VARCHAR(45) NOT NULL, ' \
                     '`video_id` VARCHAR(45) NOT NULL, ' \
                     '`title` VARCHAR(45) NOT NULL, ' \
                     '`youtube_video_link` VARCHAR(45) NOT NULL,' \
                     '`s3_link` VARCHAR(45) NULL,' \
                     '`likes` INT NULL,' \
                     '`comments_count` INT NULL,' \
                     '`thumbnail_link` VARCHAR(45) NULL,'\
                     'PRIMARY KEY (`index`),'\
                     'CONSTRAINT `youtuber_index`' \
                     'FOREIGN KEY (`index`)' \
                     'REFERENCES `sys`.`youtuber` (`index`)' \
                     'ON DELETE NO ACTION' \
                     'ON UPDATE NO ACTION);'

videos_table_query = '''
CREATE TABLE `tubescraper`.`videos` (
  `index` INT NOT NULL AUTO_INCREMENT,
  `channel_id` VARCHAR(45) NOT NULL,
  `video_id` VARCHAR(45) NOT NULL,
  `title` VARCHAR(45) NOT NULL,
  `youtube_link` VARCHAR(45) NOT NULL,
  `s3_link` VARCHAR(45) NULL,
  `likes` INT NULL,
  `comments_count` INT NULL,
  `thumbnail_link` VARCHAR(45) NULL,
  PRIMARY KEY (`index`),
  UNIQUE INDEX `video_id_UNIQUE` (`video_id` ASC) VISIBLE);
'''


youtuber_table_query = ''' /
CREATE TABLE `tubescraper`.`youtuber` (
`channel_id` VARCHAR(45) NOT NULL,
`channel_name` VARCHAR(45) NOT NULL,
PRIMARY KEY (`channel_id`),
UNIQUE INDEX `channel_id_UNIQUE` (`channel_id` ASC) VISIBLE);
'''
