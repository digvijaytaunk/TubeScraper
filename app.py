from flask import Flask, render_template, request

from scaper.youtube_resource import YoutubeResource

app = Flask(__name__, static_folder="static")

# TODO Add doc string


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        url = request.form.get('videosUrl')
        if not validate_url(url):
            return render_template('index.html', data={'status': "URL not recognised. "
                                                                 "Please provide youtube video link only. "
                                                                 "Must contain 'youtube.com/watch' string"})

        yt = YoutubeResource(url)
        result = yt.scrape()

        return render_template('result.html', data=result)


def validate_url(url: str) -> bool:
    """
    Checks if passed url contains "watch" keyword.
    :param url: str
    :return: Bool
    """
    string_to_find = 'youtube.com/watch'
    return True if string_to_find in url else False


if __name__ == '__main__':
    app.run(debug=True)
