from flask import Flask, render_template, request

app = Flask(__name__)

# TODO Add doc string


@app.get('/')
def root():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def process():
    url = request.form.get('videosUrl')
    return render_template('index.html', data=url)


if __name__ == '__main__':
    app.run(debug=True)
