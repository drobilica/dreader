from flask import Flask, render_template
import feedparser

app = Flask(__name__)

@app.route('/')

def index():
    feed_url = 'https://www.rockpapershotgun.com/feed' # Replace with your desired RSS feed URL
    feed = feedparser.parse(feed_url)
    return render_template('base.html.j2', feed=feed)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
