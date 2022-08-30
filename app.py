from flask import Flask, render_template, request

from scaper.youtube_resource import YoutubeResource

app = Flask(__name__)

# TODO Add doc string


@app.get('/')
def root():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def process():
    url = request.form.get('videosUrl')
    if not validate_url(url):
        return render_template('index.html', data={'status': "URL not recognised. Please provide youtube video link only."})

    yt = YoutubeResource(url)
    result = yt.scrape()
    return render_template('index.html', data=result)


def validate_url(url: str) -> bool:
    """
    Checks if passed url contains "watch" keyword.
    :param url: str
    :return: Bool
    """
    return True if 'watch' in url else False


if __name__ == '__main__':
    # TODO Handle this type of request "https://www.youtube.com/watch?v=8cm1x4bC610&ab_channel=Telusko"
    # Use GET request to parse variable
    app.run(debug=True)