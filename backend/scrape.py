import django
import logging
import os
import sys

import strategy.rss

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lofi_news.settings')
django.setup()

from frontend import models

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'scrape.log'),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    sources = models.DataSource.objects.all()
    logger.info("Found %s data sources", sources)
    for source in sources:
        logger.info("Fetching %s", source)
        if source.type == 'rss':
            stories = strategy.rss.scrape(source.url)
            #print(scraped)
            for story in stories:
                # TODO: check for uniqueness
                story_model = models.Story(data_source=source,
                                           title=story['title'],
                                           original_url = story['original_url'],
                                           raw_data = story['raw_data'],
                                           text = story['text'])
                story_model.save()
                logger.info("created story %s", story_model)

    