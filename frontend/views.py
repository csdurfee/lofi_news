from django.shortcuts import render
from django.template.loader import render_to_string
from .models import Story

from datastar_py.django import (DatastarResponse, ServerSentEventGenerator, 
                                read_signals)

import logging
logger = logging.getLogger(__name__)

def index(request):
    #logger.error("hoo boy")
    # TODO: validation
    # TODO: these should be coming from datastar signal, probably
    limit = request.GET.get('limit', 10)
    offset = request.GET.get('offset', 0)

    # oldest stories first
    stories = Story.objects \
                .select_related('data_source')[offset : offset+limit]
    return render(request, 'frontend/index.html', 
                  {'stories': stories})


def more(request):
    # get last viewed story id from request...

    ## still getting datastar PATCH working right
    signals = read_signals(request)
    logger.error("signals is %r" % signals)
    if signals and ('lastId' in signals):
        stories = Story.objects.filter(id__gt=signals['lastId'])[:10]
        rendered = render_to_string('frontend/stories.html',
                    {'stories': stories, 'request': request})

        return DatastarResponse(
                ServerSentEventGenerator.patch_elements(rendered)
        )
    else:
        return ""
