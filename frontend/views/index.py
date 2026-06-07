from frontend.models import Story, Vote
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from datastar_py.django import (DatastarResponse, read_signals)
from datastar_py.django import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode

import logging
logger = logging.getLogger(__name__)

def index(request):
    limit = request.GET.get('limit', 10)
    if limit > 100:
        limit = 100

    stories = list(Story.objects.order_by("-id") \
                .select_related('data_source')[:limit])

    last_id = stories[limit-1].id
    story_ids = {story.id for story in stories}

    if request.user:
        votes_on_page = Vote.by_user_and_stories(request.user.id, story_ids)
    else:
        votes_on_page = {}

    # get user settings. TODO: factor out into own UserSettings component.
    new_tabs = request.session.get('new_tabs', 0)

    logger.debug(f"new_tabs is {new_tabs}")

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
def more(request):
    signals = read_signals(request)
    logger.debug("got request %r" % request)

    if signals and ('lastId' in signals):
        lastId = signals['lastId']
        limit = 10

        stories = list(Story.objects.order_by("-id").filter(id__lt=lastId)[:limit])

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
            newLastId = stories[limit-1].id

            # we can just return an array to DatastarResponse.
            return DatastarResponse(
                [
                SSE.patch_elements(rendered,
                                    selector="#stories",
                                    mode=ElementPatchMode.APPEND
                ),
                # note: it's NOT kebab case for signals sent from server
                SSE.patch_signals(
                            {"lastId": newLastId }
                ),
                ]
            )
    else:
        logger.debug("no signal received")
        return no_stories()