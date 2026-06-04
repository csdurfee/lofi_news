from django.shortcuts import render
from .models import Story

import logging
logger = logging.getLogger(__name__)

def index(request):
    #logger.error("hoo boy")
    # TODO: validation
    # TODO: these should be coming from datastar signal, probably
    limit = request.GET.get('limit', 10)
    offset = request.GET.get('offset', 0)

    stories = Story.objects \
                .select_related('data_source') \
                .order_by('-retrieved')[offset : offset+limit]
    return render(request, 'frontend/index.html', 
                  {'stories': stories})


def more(request):
    # get last viewed story id from request...
    ...