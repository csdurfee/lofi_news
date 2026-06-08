from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from datastar_py.django import (DatastarResponse, read_signals)
from datastar_py.django import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode

from frontend.models import Story, Vote, DataSource

import logging
logger = logging.getLogger(__name__)

ALL_SOURCES = 1

def _get_stories(order_by="-id", limit=10, sources=ALL_SOURCES, last_id=None):
    # TODO: refactor this so I can dynamically add filters, so it works with /more
    query = Story.objects.order_by(order_by)
    if sources != ALL_SOURCES:
        query = query.filter(data_source__in=sources)
    if last_id:
        query = query.filter(id__lt=last_id)
    
    stories = list(query.select_related('data_source')[:limit])

    return stories


def index(request, source_code=None):
    limit = 10

    if source_code == None:
        stories = _get_stories(limit=limit)
    else:
        # get ID for source
        sources = DataSource.objects.filter(code=source_code)
        if len(sources) == 0:
            return HttpResponseNotFound()
        else:
            stories = _get_stories(limit=limit, sources=sources)

    last_id = stories[limit-1].id
    story_ids = {story.id for story in stories}

    if request.user:
        votes_on_page = Vote.by_user_and_stories(request.user.id, story_ids)
    else:
        votes_on_page = {}

    # get user settings. TODO: factor out into own UserSettings component.
    new_tabs = request.session.get('new_tabs', 0)

    return render(request, 'frontend/index.html', 
                  {'stories': stories,
                   'votes_on_page': votes_on_page,
                   'last_id': last_id,
                   'new_tabs': int(new_tabs)})

def about(request):
    text_body = "this page left intentionally blank"
    return render(request, 'frontend/index.html',
                  {'text_body': text_body})

def no_stories():
    """
    patches out the "load more" if there are no stories to load
    """
    return DatastarResponse(
        SSE.remove_elements("#load-more")
    )

@require_http_methods(['GET'])
def more(request, sources=ALL_SOURCES):
    signals = read_signals(request)
    logger.info("got signals %r" % signals)

    if signals and ('lastId' in signals):
        last_id = signals['lastId']
        limit = 10

        stories = _get_stories(sources=sources, limit=limit, last_id=last_id)

        if len(stories) == 0:
            return no_stories()
        else:
            if request.user:
                story_ids = {story.id for story in stories}
                votes_on_page = Vote.by_user_and_stories(request.user.id, story_ids)
            else:
                votes_on_page = {}
            rendered = render_to_string('frontend/stories.html',
                        {'stories': stories,
                         'votes_on_page': votes_on_page,
                         }, request=request)
            new_last_id = stories[limit-1].id

            # we can just return an array to DatastarResponse.
            return DatastarResponse(
                [
                # default mode replaces the selector; we want to add to end
                SSE.patch_elements(rendered,
                                    selector="#stories",
                                    mode=ElementPatchMode.APPEND
                ),
                # note: it's NOT kebab case for signals sent from server
                SSE.patch_signals(
                            {"lastId": new_last_id }
                ),
                ]
            )
    else:
        logger.debug("no signal received")
        return no_stories()