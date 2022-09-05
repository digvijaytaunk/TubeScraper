
class Video:
    def __init__(self, video_id, channel_id='', channel_name='', published_at='', title='', thumbnail_url='', thumbnail_base64='', likes=0, views=0, comment_count=0, watch_url='', comment_thread=[]):
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.publishedAt = published_at
        self.videoId = video_id
        self.title = title
        self.thumbnail_url = thumbnail_url
        self.thumbnail_base64 = thumbnail_base64
        self.likes = likes
        self.views = views
        self.comment_count = comment_count
        self.watch_url = watch_url
        self.comment_thread = comment_thread
        self.s3_url = ''


if __name__ == '__main__':

    url = 'https://www.youtube.com/watch?v=QXeEoD0pB3E'
    yt = Video(url)

    thumbnail_url = yt.thumbnail_url
    print(thumbnail_url)
