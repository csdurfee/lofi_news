import django
import logging
import os
import sys

import strategy.rss

# this is necessary so we can use frontend.models in another package
# (I think)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lofi_news.settings')
django.setup()

from frontend import models

# FIXME: there is probably a better way to do this...
# django's logging config will cause log events to go to the default
# django log, which we don't want. so we have to remove the existing
# log handlers.
# https://stackoverflow.com/questions/12158048/changing-loggings-basicconfig-which-is-already-set
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
LOGFILE = os.path.join(LOG_DIR, 'scrape.log')

logging.basicConfig(
    filename=LOGFILE,
    level=logging.DEBUG,
    format="{levelname} {asctime} {module} {message}",
    style="{"
    )
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger(__name__)

def main():
    sources = models.DataSource.objects.all()
    logger.info(f"Found {len(sources)} data sources")
    for source in sources:
        logger.info(f"Fetching {source}")
        if source.type == 'rss':
            stories = strategy.rss.scrape(source.url)
            for story in stories:
                # uniqueness is tested based on original URL.
                if models.Story.objects.filter(original_url=story['original_url']).exists():
                    logger.info(f"story {story['original_url']} already exists")
                else:
                    story_model = models.Story(data_source=source,
                                            title=story['title'],
                                            original_url = story['original_url'],
                                            raw_data = story['raw_data'],
                                            text = story['text'])
                    story_model.save()
                    logger.info(f"created story {story_model}")

if __name__ == '__main__':
    main()
