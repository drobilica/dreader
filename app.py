from flask import Flask, render_template
import feedparser
import yaml
import logging
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    with open("rss_feeds.yml", 'r') as stream:
        data = yaml.safe_load(stream)

    all_feeds = {}
    for group, feeds in data.items():
        group_feeds = []
        for feed_info in feeds:
            feed_url = feed_info['url']
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                soup = BeautifulSoup(entry.summary, 'html.parser')
                img_tag = soup.find('img')

                # Check if media:content is available in the feed
                media_content = entry.get('media_content', [{}])[0].get('url', None)
                
                if img_tag:
                    entry.media_thumbnail = [{"url": img_tag['src']}]
                elif media_content:
                    entry.media_thumbnail = [{"url": media_content}]
                    
                entry.summary = soup.get_text()
            group_feeds.append({"name": feed_info['name'], "entries": feed.entries})
        all_feeds[group] = group_feeds

    return render_template('base.html.j2', all_feeds=all_feeds)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
