from django.shortcuts import render
from django.template.loader import render_to_string
from .models import Story

from datastar_py.django import (DatastarResponse, ServerSentEventGenerator, 
                                read_signals)
from datastar_py.consts import ElementPatchMode

import logging
logger = logging.getLogger(__name__)

def index(request):
    #logger.error("hoo boy")

    limit = request.GET.get('limit', 10)
    # offset = request.GET.get('offset', 0)

    # oldest stories first
    stories = Story.objects \
                .select_related('data_source')[:limit]
    last_id = stories[limit-1].id
    
    return render(request, 'frontend/index.html', 
                  {'stories': stories,
                   'last_id': last_id})


def more(request):

    ## still getting datastar PATCH working right
    signals = read_signals(request)
    logger.error("signals is %r" % signals)
    if signals and ('lastId' in signals):
        stories = Story.objects.filter(id__gt=signals['lastId'])[:10]
        rendered = render_to_string('frontend/stories.html',
                    {'stories': stories, 'request': request})

        return DatastarResponse(
                ServerSentEventGenerator.patch_elements(rendered,
                                                        selector="#stories",
                                                        mode=ElementPatchMode.APPEND)
        )
    else:
        return ""
