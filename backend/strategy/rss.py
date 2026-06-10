import re

import feedparser
from bs4 import BeautifulSoup

def fetch(url):
    feed = feedparser.parse(url)
    return feed

def remove_links(text):
    return re.sub(r'https?://\S+', '', text)

def fix_no_space_after_periods(text):
    return re.sub(r"(\.)([A-Z])", r"\1 \2", text)

def get_clean_text(raw_data):
    soup = BeautifulSoup(raw_data, 'html.parser')
    clean_text = soup.get_text() \
        .strip()
    clean_text = remove_links(clean_text)
    clean_text = fix_no_space_after_periods(clean_text)

    return clean_text

def is_baloney(parsed):
    """
    Filter out entries which are ads, etc.
    """
    # reddit nonsense
    if re.search("contains content not supported", parsed['text']):
        return True
    # empty bodies
    if len(parsed['text']) < 20:
        return True
    return False

def scrape(url):
    """
    Loads the specified RSS URL and converts them to our data format.
    """
    out = []
    raw_data = fetch(url)
    for entry in raw_data.entries:
        if 'content' in entry:
            # like reddit, yahoo
            raw_data = entry.content[0].value
        else:
            # like espn
            raw_data = entry.summary

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