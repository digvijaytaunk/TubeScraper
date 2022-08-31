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

        if video_id == '' or API_KEY == '' or API_KEY is None:
            return {'status': 'Failed to process. Check Video ID or Youtube Data API Key'}

        channel_title = self.get_channel_title()
        channel_uid = self.get_channel_id()

        data = {
            'channel_title': channel_title,
            'channel_uid': channel_uid,
            'status': 'success'
        }

        return data

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

    def get_video_stats(self, video_obj, uid):
        pass

    def extract_video_id(self) -> str:
        if '?' in self._input_url:
            parts = self._input_url.split('?')
            args = parts[-1]
            args_parts = args.split('&')
            dic = {}
            for i in range(len(args_parts)):
                args_n_vals = args_parts[i].split('=')
                dic[args_n_vals[0]] = args_n_vals[1]

            return dic.get('v')

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

    details = yt.get_channel_detail_from_input_url('N182e5GNyH4')
    print(details)