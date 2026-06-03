import django
import logging
import os
import sys

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
    logger.info("Found %d data sources", sources.count())
    print(sources)

    