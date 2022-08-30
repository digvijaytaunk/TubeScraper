
class Channel:
    def __init__(self, uid):
        self._uid = uid
        self._title = ''

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value


class Video:
    def __init__(self, url):
        self._url = url
        self._uid = ''
        self._title = ''
        self._thumbnail_url = ''
        self._views = 0
        self._watch_url = ''
        self._publish_date = 0
        self._streams = []
        self._description = ''
