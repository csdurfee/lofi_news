import re

import feedparser
from bs4 import BeautifulSoup

def fetch(url):
    feed = feedparser.parse(url)
    return feed

def get_clean_text(raw_data):
    soup = BeautifulSoup(raw_data, 'html.parser')
    clean_text = soup.get_text() \
        .strip()
    # TODO: fix no space after periods?
    # regex: (\.)([A-Z]), replace with \1 \2 everywhere
    
    return clean_text

def is_baloney(parsed):
    """
    Filter out entries which are ads, etc.
    """
    # reddit nonsense
    if re.search("contains content not supported", parsed.text):
        return True
    return False

def scrape(url):
    """
    Loads the specified RSS URL and converts them to our data format.
    """
    out = []
    raw_data = fetch(url)
    for entry in raw_data.entries:
        raw_data = entry.content[0].value

        clean_text = get_clean_text(raw_data)

        parsed = dict(
            title = entry.title,
            original_url = entry.link,
            raw_data = raw_data,
            text = clean_text,
        )
        if not is_baloney(parsed):
            out.append(parsed)
    return out