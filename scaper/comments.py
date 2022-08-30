from youtube_comment_scraper_python import *


def extract_one_comment(url):
    youtube.open(url)
    response = youtube.video_comments()
    data = response['body']
    return data


def extract_multiple_comments(url):
    youtube.open(url)
    all_data = []
    for i in range(0, 5):
        response = youtube.video_comments()
        data = response['body']
        all_data.extend(data)
    return all_data


if __name__ == '__main__':
    u = "https://www.youtube.com/watch?v=QXeEoD0pB3E"
    # print(extract_one_comment(u))
    print(extract_multiple_comments(u))


