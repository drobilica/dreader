import json
import logging
from flask import Flask, render_template
import feedparser
import yaml
import redis
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
logging.basicConfig(level=logging.DEBUG)

# Connect to Redis
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

@app.route('/')
def index():
    with open("rss_feeds.yml", 'r', encoding='utf-8') as stream:
        data = yaml.safe_load(stream)

    all_feeds = {}
    new_articles_count = 0  # Keep track of how many new articles are added

    for group, feeds in data.items():
        group_feeds = []
        for feed_info in feeds:
            feed_url = feed_info['url']
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                # Use a unique identifier for each article, like the link or id
                entry_id = entry.get('id', entry.get('link'))

                # Check if the article already exists in Redis
                if r.exists(entry_id):
                    continue

                # Log how many new articles were added
                new_articles_count += 1

                # Use media:thumbnail if available
                if 'media_thumbnail' in entry:
                    continue

                # Use media:content if available
                if 'media_content' in entry and entry.media_content[0].get('url', None):
                    entry.media_thumbnail = [{"url": entry.media_content[0]['url']}]
                    continue

                # Fallback to parsing 'description' or 'summary'
                description = entry.get('description', entry.get('summary', ''))

                if isinstance(description, list):
                    description = ' '.join(description)

                soup = BeautifulSoup(description, 'html.parser')
                img_tag = soup.find('img')

                if img_tag:
                    entry.media_thumbnail = [{"url": img_tag['src']}]

                entry.summary = soup.get_text()

                # Cache the article in Redis
                r.set(entry_id, json.dumps(entry))

            group_feeds.append({"name": feed_info['name'], "entries": feed.entries})
        all_feeds[group] = group_feeds

    logging.info("%s new articles were added to Redis.",new_articles_count)

    return render_template('base.html.j2', all_feeds=all_feeds)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
