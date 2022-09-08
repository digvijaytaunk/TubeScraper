import logging

import boto3
from flask import Flask, render_template, request

from db.mongo import MongoDb
from db.sql_db import MySql
from globs import BUCKET_NAME, S3_ACCESS_KEY_ID, SECRET_ACCESS_KEY

from scaper.youtube_resource import YoutubeResource

app = Flask(__name__, static_folder="static")


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/', methods=['GET', 'POST'])
def root():
    """
    Root end point for user input form
    :return:
    """
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        url = request.form.get('videosUrl')
        count_str = request.form.get('videoCount').strip()
        upload = request.form.get('upload')
        scrape_count = _validate_count(count_str)
        app.logger.info(f'POST - Fetch request for {url}, {scrape_count} videos, Upload status - {upload}')
        if not validate_url(url):
            app.logger.warning(f'POST - Fetch request for {url}, Invalid url {url}')
            return render_template('index.html', data={'status': "URL not recognised. "
                                                                 "Please provide youtube video link only. "
                                                                 "Must contain 'youtube.com/watch' string"})

        upload_to_s3 = True if upload else False
        app.logger.info(f'Started scraping process...')
        yt = YoutubeResource(url, upload_to_s3, app.logger, scrape_count)
        result = yt.scrape()
        app.logger.info(f'Scraping process completed.')
        return render_template('result.html', data=result)


# For maintenance only
@app.route('/admin/db/reset', methods=['GET'])
def clear_mongo_collection():
    """
    For the developer to clean AWS SQL & S3 resources & MongoDB. Deletes all SQL table & mongoDB and recreate it.
    Also Deletes all files stored in S3 bucket.
    :return:
    """
    mongo_obj = MongoDb(app.logger)
    mongo_obj.reset_collection()
    sql = MySql(app.logger)
    sql.reset_tables()

    # Delete all items from bucket
    s3 = boto3.resource('s3', aws_access_key_id=S3_ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
    bucket = s3.Bucket(BUCKET_NAME)
    bucket.objects.all().delete()

    return render_template('index.html')


def validate_url(url: str) -> bool:
    """
    Checks if passed url contains "youtube.com/watch" keyword.
    :param url: str
    :return: Bool
    """
    string_to_find = 'youtube.com/watch'
    return True if string_to_find in url else False


def _validate_count(count_str: str) -> int:
    """
    Returns validate user input
    :param count_str:
    :return: int: no. of videos to fetch
    """
    if count_str == '':
        return 50
    try:
        c = int(count_str)
        count = c if 1 <= c <= 50 else 50
        return count
    except:
        return 50


if __name__ == '__main__':
    app.run(debug=True)
