import os
import base64
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Dict, List

import googleapiclient.discovery
import requests

from db.mongo import MongoDb
from db.sql_db import MySql
from globs import API_KEY, SECRET_ACCESS_KEY, S3_ACCESS_KEY_ID, BUCKET_NAME, DOWNLOAD_PATH, STATUS, ENABLE_CLOUD_DB
from scaper.video import Video
from pytube import YouTube


class YoutubeResource:
    def __init__(self, url: str, extract_stream_info: bool, logger, scrape_count: int = 50):
        self._input_url = url
        self.extract_stream_info = extract_stream_info
        self._scrape_count = scrape_count
        self.logger = logger
        self.youtube = self._build_youtube()
        self._input_video_id = self._extract_video_id()
        self._input_channel_id = self._get_channel_id_by_search_query()
        self.final_result = None
        self.download_path = DOWNLOAD_PATH
        self.s3_urls = []

    def _build_youtube(self):
        """
        Builds an API object to easily access all the available api in youtube
        :param API_KEY:
        :return:
        """
        api_service_name = "youtube"
        api_version = "v3"
        yt = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=API_KEY)

        self.logger.info('Youtube object build successfully')
        return yt

    def _input_channel_response(self) -> Dict:
        """
       Fetch all the available data from Youtube API related to provided Channel
       :return: Dict
       """

    def _input_video_response(self) -> Dict:
        """
        Fetch all the available data from Youtube API related to provided video
        :return: Dict
        """
        try:
            request = self.youtube.videos().list(part="snippet,contentDetails,statistics", id=self._input_video_id)
            res = request.execute()
            self.logger.info(f'Response for input URL: {res}')
            return res
        except Exception as e:
            return {}

    def get_channel_id(self):
        """
        Get channel ID from input video ID or Videos URL or channel main page URL
        :return: str: channel id
        """
        if self._input_video_id:
            res = self._input_video_response()
            channel_id = res['items'][0]['snippet']['channelId']
            self.logger.info(f'Fetched channel id from Video ID - {channel_id}.')
            self._input_channel_id = channel_id
            return channel_id

        if self._input_channel_id:
            self.logger.info(f'Fetched channel id from Search URL- {self._input_channel_id}.')
            return self._input_channel_id

    def get_channel_title(self):
        """
        Get channel title from channel ID
        :return: str: channel title
        """

        request = self.youtube.activities().list(
            part="snippet",
            channelId=self._input_channel_id,
            maxResults=10,
        )
        response = request.execute()
        title = response['items'][0]['snippet']['channelTitle']
        self.logger.info(f'Fetched channel title - {title}.')
        return title

    def scrape(self) -> Dict:
        """
        Public method to start all data processing
        :return:
        """

        video_id = self._input_video_id
        channel_id = self._input_channel_id

        if (video_id == '' and channel_id == '') or API_KEY == '' or API_KEY is None:
            return {'status': 'Failed to process. Check Video or channel URL or Youtube Data API Key'}

        channel_uid = self.get_channel_id()
        channel_title = self.get_channel_title()

        video_object_list = self._get_videos_info(channel_uid)
        sql_obj = MySql(self.logger)

        if ENABLE_CLOUD_DB:
            if sql_obj.get_cursor():
                youtuber_save_status = sql_obj.save_youtuber_data(video_object_list[0])
                videos_save_status = sql_obj.save_videos(video_object_list)

                mongo_obj = MongoDb(self.logger)
                save_comments_status = mongo_obj.save_comments(video_object_list)

            else:
                youtuber_save_status = {'status': STATUS.FAIL}
                videos_save_status = {'status': STATUS.FAIL}

            if self.extract_stream_info:
                self._upload_to_s3(video_object_list)

                video_object_list = self._map_s3_url(video_object_list)
                sql_obj.update_s3_address(video_object_list)
        else:
            youtuber_save_status = {'status': 'Disabled by Admin'}
            videos_save_status = {'status': 'Disabled by Admin'}

        data = {
            'channel_title': channel_title,
            'channel_uid': channel_uid,
            'videos': video_object_list,
            'vidCount': len(video_object_list),
            'youtuber_save_status': youtuber_save_status['status'],
            'video_save_status': videos_save_status['status'],
            'status': 'success'
        }
        self.final_result = data
        return data

    def _get_videos_info(self, channel_id) -> List[Video]:
        """
        Collect all required data from the channel ID and make a list Video object.
        :param channel_id: str: Id of channel
        :return: List[Video]: List of video objects containing all necessary data.
        """
        videos = self.get_latest_published_video(channel_id)
        result = []

        try:
            for video in videos:
                video_id = video['contentDetails']['upload']['videoId']
                title = video['snippet']['title']
                thumbnail_url = video['snippet']['thumbnails']['high']['url'],
                watch_url = f'https://www.youtube.com/watch?v={video_id}'

                stats = self.get_video_statistics(video_id)
                comments = self.get_comments(video_id)

                res = requests.get(thumbnail_url[0])
                base64_format = base64.b64encode(res.content).decode("utf-8")

                if self.extract_stream_info:
                    self._download(watch_url, video_id)

                v = Video(
                    video_id=video_id,
                    channel_id=video['snippet']['channelId'],
                    channel_name=video['snippet']['channelTitle'],
                    published_at=datetime.fromisoformat(video['snippet']['publishedAt']),
                    title=title,
                    thumbnail_url=thumbnail_url[0],
                    thumbnail_base64=base64_format,
                    likes=stats['likes'],
                    views=stats['views'],
                    comment_count=stats['comment_count'],
                    watch_url=watch_url,
                    comment_thread=comments
                )
                result.append(v)

        except Exception as e:
            self.logger.error(f'Error occurred while fetching Video info - {e}')

        self.logger.info(f'Video info - {result}')
        return result

    def get_video_statistics(self, video_id: str) -> Dict:
        """
        Extract video statistics from youtube data api for a video
        :param video_id: str: id of video
        :return: Dict{views: int, likes: int, comment_count: int} Dictionary with key - views, likes, comment_count
        """
        self.logger.info(f'Fetching video stats for id - {video_id}')
        request = self.youtube.videos().list(
            part="statistics",
            id=video_id
        )
        response = request.execute()

        dic = {
            'views': int(response['items'][0]['statistics']['viewCount']),
            'likes': int(response['items'][0]['statistics']['likeCount']),
            'comment_count': int(response['items'][0]['statistics']['commentCount'])
        }
        self.logger.info(f'Video stats - {dic}')
        return dic

    def get_comments(self, video_id) -> List[Dict]:
        """
        Extract all comments along with thread of provided video id
        :param video_id: ID of video
        :return: List[Dict{comment_author, message}]: List of dictionary with key - 'comment_author' & 'message'
        """
        self.logger.info(f'Fetching video comments for id - {video_id}')
        request = self.youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id
        )
        response = request.execute()
        response_list = response['items']
        comments_list = []

        while response.get('nextPageToken'):
            request = self.youtube.commentThreads().list(part="snippet,replies",
                                                         videoId=video_id,
                                                         pageToken=response['nextPageToken'])
            response = request.execute()
            response_list.extend(response['items'])

        for item in response_list:
            top_level_msg = item['snippet']['topLevelComment']['snippet']['textDisplay']
            top_level_auther = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            top_level_date = item['snippet']['topLevelComment']['snippet']['publishedAt']
            replies = []
            if item['snippet']['totalReplyCount'] > 0:
                for reply in item['replies']['comments']:
                    msg = reply['snippet']['textDisplay']
                    author = reply['snippet']['authorDisplayName']
                    # reply_date = reply['snippet']['publishedAt']
                    replies.append({'comment_author': author, 'message': msg})
            data = {'top_msg': top_level_msg, 'top_author': top_level_auther,
                    'replies': replies}  # 'data':top_level_date
            comments_list.append(data)

        self.logger.info(f'Comments for id - {video_id} is - {comments_list}')
        return comments_list

    def get_latest_published_video(self, channel_id: str) -> List[Dict]:
        """
        Return a list of latest 50 videos sorted based on published date.
        :param channel_id: ID of the video passed through the html form
        :return: List[Dict]: List of Dictionary of snippet received from Data API
        """
        self.logger.info(f'Fetching latest published video for channel id - {channel_id}')
        all_videos_data = self.get_all_videos_from_response(channel_id)
        sorted_by_date = list(
            reversed(sorted(all_videos_data, key=lambda vid: datetime.fromisoformat(vid['snippet']['publishedAt']))))
        self.logger.info(f'All published video for channel id - {sorted_by_date}')
        return sorted_by_date[:self._scrape_count]

    def get_all_videos_from_response(self, channel_id: str) -> List[Dict]:
        """
        Extract all video data from response object from Youtube Data API
        :param channel_id: str: Channel ID
        :return:
        """
        self.logger.info(f'Fetching all video for channel id - {channel_id}')
        request = self.youtube.activities().list(
            part="snippet, contentDetails",
            channelId=channel_id,
            maxResults=50,
        )
        response = request.execute()
        all_videos = response['items']

        while response.get('nextPageToken'):
            request = self.youtube.activities().list(part="contentDetails",
                                                     channelId=channel_id,
                                                     pageToken=response['nextPageToken'])
            response = request.execute()
            all_videos.extend(response['items'])

        self.logger.info(f'All videos for channel id - {channel_id} is {all_videos}')
        return all_videos

    def get_channel_detail_from_input_url(self, v_id: str) -> Dict:
        """
        Extract Channel ID & Channel Title from provided video ID and return a dictionary
        :param v_id: video ID
        :return: {channel_id: value, channel_title: value}
        """
        try:
            self.logger.info(f'Fetching channel details for video id - {v_id}')
            request = self.youtube.videos().list(part="snippet,contentDetails,statistics", id=v_id)
            res = request.execute()

            first_item = res['items'][0]
            channel_id = first_item['snippet']['channelId']
            channel_title = first_item['snippet']['channelTitle']
            self.logger.info(f'Channel details for first video - {first_item}')
            return {'channel_id': channel_id, 'channel_title': channel_title}
        except Exception as e:
            self.logger.error(f'Failed to fetch channel details from video ID - {v_id}. {e}')
            return {}

    def _download(self, url: str, file_name: str):
        pyt = YouTube(url)
        try:
            self.logger.info(f'Fetching stream data for video from url - {url}')
            streams = pyt.streams

            # stream = streams.get_by_resolution('144p')  # Video resolution i.e. "720p", "480p", "360p", "240p", "144p"
            strms = streams.filter(progressive=False)  # Video resolution i.e. "720p", "480p", "360p", "240p", "144p"
            stream = strms[0]
            ext = '.3gpp'
            if stream is None:
                stream = streams.get_by_resolution('240p')
                ext = 'mp4'
            if stream is None:
                stream = streams.get_by_resolution('360p')
                ext = 'mp4'
            if stream is None:
                stream = streams.get_by_resolution('480p')
                ext = 'mp4'
            self.logger.info(f'Downloading video from stream - {stream}')
            stream.download(output_path=self.download_path, filename=f'{file_name}{ext}')
        except Exception as e:
            self.logger.error(f'Failed to download video from url - {url}. {e}')

    def _upload_to_s3(self, videos: List[Video]):
        self.logger.info(f'Uploading to S3 initiated.')
        client = boto3.client('s3', aws_access_key_id=S3_ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
        bucket_location = client.get_bucket_location(Bucket=BUCKET_NAME)
        files_to_upload = [video.videoId for video in videos]

        for filename in os.listdir(self.download_path):
            if filename.split('.')[0] not in files_to_upload:
                continue

            f = os.path.join(self.download_path, filename)
            if os.path.isfile(f):
                try:
                    self.logger.info(f'Uploading file - {f}')
                    client.upload_file(f, BUCKET_NAME, filename)
                    object_url = f'https://s3-{bucket_location["LocationConstraint"]}.amazonaws.com/{BUCKET_NAME}/{filename}'
                    self.s3_urls.append(object_url)
                    self.logger.info(f'S3 url - {object_url}')

                except ClientError as e:
                    self.logger.error(f'Invalid credentials {e}')

                except Exception as e:
                    self.logger.error(f'Failed to upload to S3 - {f}. {e}')

    def _extract_video_id(self) -> str:
        watch_url = 'youtube.com/watch'

        if watch_url in self._input_url:
            return self._extract_video_id_from_v_param()

        return ''

    def _get_channel_id_by_search_query(self) -> str:
        """
        Return channel ID from Youtube Data API using search endpoint
        :return: str
        """
        channel_url = ['/c/', '/user/', '/channel/']

        # Hardcoded because unable to find Hitesh Chaudhry's channel with channel URL.
        if 'HiteshChoudharydotcom' in self._input_url:
            return 'UCXgGY0wkgOzynnHvSEVmE3A'

        for tag in channel_url:
            if tag in self._input_url:
                search_tag = self._get_search_tag_from_url()
                request = self.youtube.search().list(part="snippet", maxResults=5, q=search_tag)
                res = request.execute()
                if res:
                    return res['items'][0]['snippet']['channelId']

        return ''

    def _get_search_tag_from_url(self) -> str:
        """
        Returns text passed in url as a search identifier for channel.
        f.ex. Returns 'krishnaik06' in https://www.youtube.com/user/krishnaik06
        f.ex. Returns 'Telusko' in https://www.youtube.com/c/Telusko
        f.ex. Returns 'UCjWY5hREA6FFYrthD0rZNIw' in https://www.youtube.com/channel/UCjWY5hREA6FFYrthD0rZNIw
        f.ex. Returns 'HiteshChoudharydotcom' in https://www.youtube.com/c/HiteshChoudharydotcom
        f.ex. Returns 'saurabhexponent1' in https://www.youtube.com/user/saurabhexponent1/videos

        :return: str
        """
        youtube_split = self._input_url.split('/')
        youtube_index = [youtube_split.index(item) for item in youtube_split if 'youtube' in item][0]

        return youtube_split[youtube_index + 2]

    def _extract_video_id_from_v_param(self) -> str:
        """
        Function to extract value of 'v' parameter from url provided in html form
        :return: str: id of video
        """
        self.logger.info(f'Extracting video ID from {self._input_url}.')
        if '?' in self._input_url:
            parts = self._input_url.split('?')
            args = parts[-1]
            args_parts = args.split('&')
            dic = {}
            for i in range(len(args_parts)):
                args_n_vals = args_parts[i].split('=')
                dic[args_n_vals[0]] = args_n_vals[1]
            i = dic.get('v')
            self.logger.info(f'Video ID from {self._input_url} - {i}.')
            return i

    def _map_s3_url(self, videos: List[Video]) -> List[Video]:
        for url in self.s3_urls:
            file_name = url.split('/')[-1]
            file_name_without_ext = file_name.split('.')[0]
            obj = [video for video in videos if video.videoId == file_name_without_ext]
            if len(obj) == 1:
                obj[0].s3_url = url
        self.logger.info(f'S3 mapped video list is - {videos}.')
        return videos


if __name__ == "__main__":
    url = 'https://www.youtube.com/watch?v=QXeEoD0pB3E'
    vid = '3NfjY7ddHz8'
    yt = YoutubeResource(url, True)
    # res = yt._input_video_response()
    #
    # t = yt.get_channel_title()
    # id = yt.get_channel_id()
    # print(t, id)
    #
    # details = yt.get_channel_detail_from_input_url('N182e5GNyH4')
    # print(details)
    #
    # d = yt.get_video_statistics(vid)
    # print(d)

    # yt._download(url)

    yt._upload_to_s3()
