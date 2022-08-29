from pytube import YouTube


class YtVideo:
    def __init__(self, url: str):
        self._url = url
        self._yt_obj = YouTube(self._url)

    @property
    def thumbnail_url(self):
        return self._yt_obj.thumbnail_url

    @property
    def available_quality(self):
        return self._yt_obj.streams

    def download(self):
        first = self._yt_obj.streams.first()
        output_path = 'dump/'
        first.download(output_path=output_path)


if __name__ == '__main__':

    url = 'https://www.youtube.com/watch?v=QXeEoD0pB3E'
    yt = YtVideo(url)
    yt.download()

    thumbnail_url = yt.thumbnail_url
    print(thumbnail_url)
