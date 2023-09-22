import json
import logging
from flask import Flask, render_template
import feedparser
import yaml
import redis
from bs4 import BeautifulSoup

# Constants
RSS_FEEDS_FILE = "rss_feeds.yml"
REDIS_HOST = 'redis'  # Change this to your Redis host
REDIS_PORT = 6379
REDIS_DB = 0

# Setup
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
logging.basicConfig(level=logging.DEBUG)

# Initialize Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def load_feeds_from_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as stream:
        return yaml.safe_load(stream)

def parse_feed(feed_url):
    return feedparser.parse(feed_url)

def extract_or_parse_image(entry):
    # Check if 'media:thumbnail' or 'media_thumbnail' already contains a URL
    if 'media_thumbnail' in entry and entry['media_thumbnail'][0].get('url', None):
        return

    # Check if 'media:content' or 'media_content' contains an image URL
    media_content_key = 'media:content' if 'media:content' in entry else 'media_content'
    if media_content_key in entry:
        first_media = entry[media_content_key][0]
        if first_media.get('url', None):
            entry['media:thumbnail'] = [{"url": first_media['url']}]
            return
    
    # If no image found yet, parse the description or summary
    description = entry.get('description', entry.get('summary', ''))
    soup = BeautifulSoup(description, 'html.parser')
    img_tag = soup.find('img')
    
    if img_tag:
        entry['media:thumbnail'] = [{"url": img_tag['src']}]
    
    entry['summary'] = soup.get_text()

def fetch_and_cache_articles(group, feeds):
    group_feeds = []

    for feed_info in feeds:
        feed = parse_feed(feed_info['url'])
        entries = []
        article_count = 0  # Initialize article count for this feed

        for entry in feed.entries:
            entry_id = entry.get('id', entry.get('link'))

            if not r.exists(entry_id):
                extract_or_parse_image(entry)
                r.set(entry_id, json.dumps(entry))

            entries.append(entry)
            article_count += 1  # Increment article count for this feed

        # Set the article count in Redis with the key as "{feed_name}_article_count"
        r.set(f"{feed_info['name']}_article_count", article_count)

        group_feeds.append({"name": feed_info['name'], "entries": entries})

    # Store the entire group in Redis as well
    r.set(group, json.dumps(group_feeds))

    return group_feeds


@app.route('/')
def index():
    feed_data = load_feeds_from_yaml(RSS_FEEDS_FILE)
    all_feeds = {}

    for group, feeds in feed_data.items():
        cached_group = r.get(group)

        if cached_group:
            logging.info(f"Fetching articles for group {group} from Redis.")
            all_feeds[group] = json.loads(cached_group)
        else:
            logging.info(f"Fetching articles for group {group} from the web.")
            group_feeds = fetch_and_cache_articles(group, feeds)
            all_feeds[group] = group_feeds

    return render_template('base.html.j2', all_feeds=all_feeds)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
