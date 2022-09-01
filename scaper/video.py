# from pytube import YouTube
#
#
# class YtVideo:
#     def __init__(self, url: str):
#         self._url = url
#         self._yt_obj = YouTube(self._url)
#
#     @property
#     def thumbnail_url(self):
#         return self._yt_obj.thumbnail_url
#
#     @property
#     def available_quality(self):
#         return self._yt_obj.streams
#
#     def download(self):
#         first = self._yt_obj.streams.first()
#         output_path = 'dump/'
#         first.download(output_path=output_path)

class Video:
    def __init__(self, video_id, uuid, channel_id='', channel_name='', published_at='', title='', thumbnail_url='', likes=0, views=0, comment_count=0, watch_url='', comment_thread=[]):
        self.uuid = uuid
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.publishedAt = published_at
        self.videoId = video_id
        self.title = title
        self.thumbnail_url = thumbnail_url
        self.likes = likes
        self.views = views
        self.comment_count = comment_count
        self.watch_url = watch_url
        self.comment_thread = comment_thread


if __name__ == '__main__':

    url = 'https://www.youtube.com/watch?v=QXeEoD0pB3E'
    yt = Video(url)

    thumbnail_url = yt.thumbnail_url
    print(thumbnail_url)
