from typing import Dict

import googleapiclient.discovery

from globs import API_KEY


class YoutubeResource:
    def __init__(self, url):
        self._input_url = url
        self._input_video_id = self.extract_video_id()
        self.youtube = self._build_youtube()

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
        except:
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
        video_id = self.extract_video_id()
        if video_id == '':
            return {}  # TODO make blank Data Object

        if API_KEY == '' or API_KEY is None:
            return {'status': 'Failed to get Youtube API key'}

        channel_title = self.get_channel_title()
        channel_uid = self.get_channel_id()

        data = {
            'channel_title': channel_title,
            'channel_uid': channel_uid,
            'status': 'success'
        }

        return data

        # channel_title = video['snippet']['channelTitle']
        # no_of_views = response['items'][0]['statistics']['viewCount']
        # likes = response['items'][0]['statistics']['likeCount']

    def get_channel_detail_from_input_url(self, vid):
        try:
            request = self.youtube.videos().list(part="snippet,contentDetails,statistics", id=vid)
            res = request.execute()
            channel_id = res['items']['snippet']['channelId']
            channel_title = res['items']['snippet']['channelTitle']
            return {'channel_id': channel_id, 'channel_title': channel_title}
        except Exception as e:
            print(e)
            return {}

    def get_video_stats(self, video_obj, uid):
        pass

    def extract_video_id(self) -> str:
        if 'watch?' in self._input_url:
            parts = self._input_url.split("?")
            value = parts[-1].split("v=")
            return value[-1] if len(value) > 0 else ''

    def get_channel_activities(self):
        pass

    def get_channel_from_video_id(self):
        request = self.youtube.videos().list(part="statistics", id=self._input_url)
        response = request.execute()


if __name__ == "__main__":
    url = 'https://www.youtube.com/watch?v=3NfjY7ddHz8'
    yt = YoutubeResource(url)
    res = yt._input_video_response()
    # print(res)
    t = yt.get_channel_title()
    id = yt.get_channel_id()
    print(t, id)