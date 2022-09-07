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
from globs import API_KEY, SECRET_ACCESS_KEY, S3_ACCESS_KEY_ID, BUCKET_NAME
from scaper.video import Video
from pytube import YouTube


# TODO split this file into 2 files. 1 file contains all that calls youtube api
class YoutubeResource:
    def __init__(self, url: str, extract_stream_info: bool, scrape_count: int = 50):
        self._input_url = url
        self.extract_stream_info = extract_stream_info
        self._scrape_count = scrape_count
        self._input_video_id = self._extract_video_id()
        self.youtube = self._build_youtube()
        self.final_result = None
        self.download_path = '~/Downloads'
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
        return yt

    def _input_video_response(self) -> Dict:
        """
        Fetch all the available data from Youtube API related to provided video
        :return: Dict
        """
        try:
            request = self.youtube.videos().list(part="snippet,contentDetails,statistics", id=self._input_video_id)
            res = request.execute()
            return res
        except Exception as e:
            return {}

    def get_channel_id(self):
        """
        Get channel ID from input video
        :return: str: channel id
        """
        res = self._input_video_response()
        return res['items'][0]['snippet']['channelId']

    def get_channel_title(self):
        """
        Get channel title from input video
        :return: str: channel title
        """
        res = self._input_video_response()
        return res['items'][0]['snippet']['channelTitle']

    def scrape(self) -> Dict:
        """
        Public method to start all data processing
        :return:
        """
        video_id = self._extract_video_id()

        if video_id == '' or API_KEY == '' or API_KEY is None:
            return {'status': 'Failed to process. Check Video ID or Youtube Data API Key'}

        channel_title = self.get_channel_title()
        channel_uid = self.get_channel_id()

        video_object_list = self._get_videos_info(channel_uid)
        sql_obj = MySql()
        youtuber_save_status = sql_obj.save_youtuber_data(video_object_list[0])
        videos_save_status = sql_obj.save_videos(video_object_list)  # TODO SQL syntex error

        mongo_obj = MongoDb()
        save_comments_status = mongo_obj.save_comments(video_object_list)

        if self.extract_stream_info:
            self._upload_to_s3()

        self._map_s3_url(video_object_list)

        data = {
            'channel_title': channel_title,
            'channel_uid': channel_uid,
            'videos': video_object_list,
            'vidCount': len(video_object_list),
            'youtuber_save_status': youtuber_save_status['status'],
            'video_save_status': videos_save_status,
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
            print(e)
        return result

    def get_video_statistics(self, video_id: str) -> Dict:
        """
        Extract video statistics from youtube data api for a video
        :param video_id: str: id of video
        :return: Dict{views: int, likes: int, comment_count: int} Dictionary with key - views, likes, comment_count
        """
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

        return dic

    def get_comments(self, video_id) -> List[Dict]:
        """
        Extract all comments along with thread of provided video id
        :param video_id: ID of video
        :return: List[Dict{comment_author, message}]: List of dictionary with key - 'comment_author' & 'message'
        """
        request = self.youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id
        )
        response = request.execute()

        comments_list = []

        for item in response['items']:
            top_level_msg = item['snippet']['topLevelComment']['snippet']['textDisplay']
            top_level_auther = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            top_level_date = item['snippet']['topLevelComment']['snippet']['publishedAt']
            replies = []
            if item['snippet']['totalReplyCount'] > 0:
                for reply in item['replies']['comments']:
                    msg = reply['snippet']['textDisplay']
                    author = reply['snippet']['authorDisplayName']
                    # reply_date = reply['snippet']['publishedAt']
                    replies.append({'comment_auther': author, 'message': msg})
            data = {'top_msg': top_level_msg, 'top_author': top_level_auther, 'replies': replies}  # 'data':top_level_date
            comments_list.append(data)
        return comments_list

    def get_latest_published_video(self, channel_id: str) -> List[Dict]:
        """
        Return a list of latest 50 videos sorted based on published date.
        :param channel_id: ID of the video passed through the html form
        :return: List[Dict]: List of Dictionary of snippet received from Data API
        """
        all_videos_data = self.get_all_videos_from_response(channel_id)
        sorted_by_date = list(reversed(sorted(all_videos_data, key=lambda vid: datetime.fromisoformat(vid['snippet']['publishedAt']))))
        return sorted_by_date[:self._scrape_count]

    def get_all_videos_from_response(self, channel_id: str) -> List[Dict]:
        """
        Extract all video data from response object from Youtube Data API
        :param channel_id: str: Channel ID
        :return:
        """
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

        return all_videos

    def get_channel_detail_from_input_url(self, v_id: str) -> Dict:
        """
        Extract Channel ID & Channel Title from provided video ID and return a dictionary
        :param v_id: video ID
        :return: {channel_id: value, channel_title: value}
        """
        try:
            request = self.youtube.videos().list(part="snippet,contentDetails,statistics", id=v_id)
            res = request.execute()

            first_item = res['items'][0]
            channel_id = first_item['snippet']['channelId']
            channel_title = first_item['snippet']['channelTitle']

            return {'channel_id': channel_id, 'channel_title': channel_title}
        except Exception as e:
            print(e)
            return {}

    def _download(self, url: str, file_name: str):
        pyt = YouTube(url)
        try:
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
            stream.download(output_path=self.download_path, filename=f'{file_name}{ext}')
        except Exception as e:
            print(e)

    def _upload_to_s3(self):
        client = boto3.client('s3', aws_access_key_id=S3_ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
        bucket_location = client.get_bucket_location(Bucket=BUCKET_NAME)

        for filename in os.listdir(self.download_path):
            f = os.path.join(self.download_path, filename)
            if os.path.isfile(f):
                try:
                    client.upload_file(f, BUCKET_NAME, filename)
                    object_url = f'https://s3-{bucket_location["LocationConstraint"]}.amazonaws.com/{BUCKET_NAME}/{filename}'
                    self.s3_urls.append(object_url)

                except ClientError as e:
                    print(f'invalid credentials {e}')
                except Exception as e:
                    print(f'{e}')

    def _extract_video_id(self) -> str:
        """
        Function to extract value of 'v' parameter from url provided in html form
        :return: str: id of video
        """
        if '?' in self._input_url:
            parts = self._input_url.split('?')
            args = parts[-1]
            args_parts = args.split('&')
            dic = {}
            for i in range(len(args_parts)):
                args_n_vals = args_parts[i].split('=')
                dic[args_n_vals[0]] = args_n_vals[1]

            return dic.get('v')

    def _map_s3_url(self, videos: List[Video]) -> List[Video]:
        for url in self.s3_urls:
            file_name = url.split('/')[-1]
            file_name_without_ext = file_name.split('.')[0]
            obj = [video for video in videos if video.videoId == file_name_without_ext]
            if len(obj) == 1:
                obj[0].s3_url = url

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
