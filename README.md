NOSQL RSS Feed Web App 
Introduction

This web application is designed to fetch, cache, and display articles from various RSS feeds. It's built using Python with the Flask framework and uses Redis for caching. The purpose is to provide a quick overview of various topics by pulling in articles from multiple sources.

System Architecture
System Architecture
Components

    Web Application: Built using Flask, serves the frontend and contains the logic to fetch and cache articles.
    Redis: In-memory data store used for caching the articles.
    RSS Feeds: The web application fetches articles from these feeds.

Data Flow

    User opens the web application.
    Flask checks Redis to see if the articles for each group exist.
    If not, Flask fetches articles from the RSS feeds and stores them in Redis.
    Flask pulls the cached articles from Redis and displays them to the user.

Communication Flow

    Web App → Redis: Store/check articles and their count.
    Web App → RSS Feeds: Fetch articles if not in Redis.
    Web App → User: Display articles.

User Flow

    First Visit: All articles are fetched from the web and cached in Redis. Articles are displayed to the user.
    Subsequent Visits: Articles are fetched from Redis and displayed. If new articles are published, they will be fetched and updated in Redis.

Code Overview
Key Functions

    load_feeds_from_yaml(): Reads the RSS feed URLs from a YAML file.
    parse_feed(): Uses the feedparser library to fetch articles from a given RSS feed URL.
    extract_or_parse_image(): Tries to find an image for each article, either from its metadata or by parsing its content.
    fetch_and_cache_articles(): Fetches articles for each group and caches them in Redis.

Caching Strategy

Redis keys are set as follows:

    {group}: Contains all articles for a group (e.g., 'Tech', 'Sports').
    {feed_name}_article_count: Contains the count of articles for a specific feed (e.g., 'Forbes_article_count').

Dependencies

    Python 3.x
    Flask
    Redis
    feedparser
    BeautifulSoup
    PyYAML

How to Run

    Install all dependencies.
    Run Redis on the default port.
    Run app.py to start the Flask application.
    Open the web browser and go to http://localhost:5000.

Future Improvements

    Add pagination.
    Implement search functionality.

Conclusion

This web application serves as a consolidated platform for accessing articles from various topics and sources. Using Redis for caching makes the application more efficient by reducing the need to fetch articles from the web on every visit.


![GraphViz Diagram](./path/to/graphviz.svg)