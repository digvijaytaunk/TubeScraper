from datetime import datetime
from typing import Dict, List
from uuid import uuid4

import googleapiclient.discovery

from db.sql_db import MySql
from globs import API_KEY
from scaper.video import Video


# TODO split this file into 2 files. 1 file contains all that calls youtube api
class YoutubeResource:
    def __init__(self, url):
        self._input_url = url
        self._input_video_id = self._extract_video_id()
        self.youtube = self._build_youtube()
        self.final_result = None

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

    def _input_video_response(self):
        try:
            request = self.youtube.videos().list(part="snippet,contentDetails,statistics", id=self._input_video_id)
            res = request.execute()
            return res
        except Exception as e:
            return {}

    def get_channel_id(self):
        res = self._input_video_response()
        return res['items'][0]['snippet']['channelId']

    def get_channel_title(self):
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

        data = {
            'channel_title': channel_title,
            'channel_uid': channel_uid,
            'videos': video_object_list,
            'vidCount': len(video_object_list),
            'youtuber_save_status': youtuber_save_status['status'],
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
                stats = self.get_video_statistics(video_id)
                comments = self.get_comments(video_id)
                v = Video(
                    video_id=video_id,
                    uuid=uuid4(),
                    channel_id=video['snippet']['channelId'],
                    channel_name=video['snippet']['channelTitle'],
                    published_at=datetime.fromisoformat(video['snippet']['publishedAt']),
                    title=video['snippet']['title'],
                    thumbnail_url=video['snippet']['thumbnails']['high']['url'],
                    likes=stats['likes'],
                    views=stats['views'],
                    comment_count=stats['comment_count'],
                    watch_url=f'https://www.youtube.com/watch?v={video_id}',
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
            part="snippet",
            videoId=video_id
        )
        response = request.execute()
        comments_list = []
        for item in response['items']:
            msg = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comment_auther = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments_list.append({
                'comment_author': comment_auther,
                'message': msg
            })
        return comments_list

    def get_latest_published_video(self, channel_id: str) -> List[Dict]:
        """
        Return a list of latest 50 videos sorted based on published date.
        :param channel_id: ID of the video passed through the html form
        :return: List[Dict]: List of Dictionary of snippet received from Data API
        """
        all_videos_data = self.get_all_videos_from_response(channel_id)
        sorted_by_date = list(reversed(sorted(all_videos_data, key=lambda vid: datetime.fromisoformat(vid['snippet']['publishedAt']))))
        return sorted_by_date[:50]

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


if __name__ == "__main__":
    url = 'https://www.youtube.com/watch?v=3NfjY7ddHz8'
    vid = '3NfjY7ddHz8'
    yt = YoutubeResource(url)
    res = yt._input_video_response()

    t = yt.get_channel_title()
    id = yt.get_channel_id()
    print(t, id)

    details = yt.get_channel_detail_from_input_url('N182e5GNyH4')
    print(details)

    d = yt.get_video_statistics(vid)
    print(d)
