from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from datastar_py.django import (DatastarResponse, read_signals)
from datastar_py.django import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode

from frontend.models import Story, Vote, DataSource

import logging
logger = logging.getLogger(__name__)

def _get_stories(request, source_code=None):
    if request.user:
        user_id = request.user.id
    else:
        user_id = None

    if source_code:
        sources = DataSource.objects.filter(code=source_code)
        if len(sources) == 0:
            return HttpResponseNotFound()
    else:
        sources = None

    signals = read_signals(request)
    if signals and ('lastId' in signals):
        last_id = signals['lastId']
    else:
        last_id = None

    stories = Story.unskipped(user_id=user_id, sources=sources, last_id=last_id)

    return stories

def _get_votes(request, story_ids=None):
    if request.user and story_ids:
        votes_on_page = Vote.by_user_and_stories(request.user.id, story_ids)
    else:
        votes_on_page = {}
    return votes_on_page

def _render_html(request, stories, votes_on_page,
                                last_id, new_tabs, source_code):
    return render(request, 'frontend/index.html',
                {'stories': stories,
                'votes_on_page': votes_on_page,
                'last_id': last_id,
                'new_tabs': int(new_tabs),
                'source_code': source_code,
                })

def _render_datastar(request, stories, votes_on_page,
                                last_id, new_tabs, source_code):
    rendered = render_to_string('frontend/stories.html',
                        {'stories': stories,
                        'votes_on_page': votes_on_page,
                        'last_id': last_id,
                        'new_tabs': int(new_tabs),
                        'source_code': source_code,
                        }, request=request)

    if len(stories) == 0:
        return _no_stories()

    new_last_id = stories[len(stories) - 1].id

    return DatastarResponse(
        [
        # default mode replaces the selector; we want to add to end
        SSE.patch_elements(rendered,
                            selector="#main-content",
                            mode=ElementPatchMode.APPEND
        ),
        # note: it's NOT kebab case for signals sent from server
        SSE.patch_signals(
                    {"lastId": new_last_id }
        ),
        ]
    )

def _no_stories():
    """
    patches out the "load more" if there are no stories to load
    """
    return DatastarResponse(
        SSE.remove_elements("#load-more")
    )

@require_http_methods(['GET'])
def index(request, source_code=None, more=False):
    limit = 10

    stories = _get_stories(request, source_code)

    # FIXME: handle if there are no stories
    last_id = stories[len(stories) - 1].id
    story_ids = {story.id for story in stories}

    votes_on_page = _get_votes(request, story_ids)

    # get user settings. TODO: factor out into own UserSettings component.
    new_tabs = request.session.get('new_tabs', 0)

    if more:
        return _render_datastar(request, stories, votes_on_page,
                                last_id, new_tabs, source_code)
    else:
        return _render_html(request, stories, votes_on_page,
                                last_id, new_tabs, source_code)

@require_http_methods(['GET'])
def more(request, source_code=None):
    # this needs to check if signal exists.
    # if it doesn't, return no more stories to stop load more
    signals = read_signals(request)
    if not signals:
        return _no_stories()
    else:
        return index(request, source_code=source_code, more=True)

def about(request):
    text_body = "this page left intentionally blank"
    return render(request, 'frontend/index.html',
                  {'text_body': text_body})
