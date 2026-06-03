import feedparser
from bs4 import BeautifulSoup

def fetch(url):
    feed = feedparser.parse(url)
    return feed

def scrape(url):
    """
    Loads the specified RSS URL and converts them to our data format.
    """
    out = []
    raw_data = fetch(url)
    for entry in raw_data.entries:
        raw_data = entry.content[0].value
        soup = BeautifulSoup(raw_data, 'html.parser')
        parsed = dict(
            title = entry.title,
            original_url = entry.link,
            raw_data = raw_data,
            text = soup.get_text(),
        )
        out.append(parsed)
    return out