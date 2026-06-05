from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, Http404
from django.views.decorators.http import require_http_methods

from .models import Story

from datastar_py.django import (DatastarResponse, read_signals)
from datastar_py.django import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode

import logging
logger = logging.getLogger(__name__)

def join(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'frontend/join.html', {'form': form})

def index(request):
    limit = request.GET.get('limit', 10)
    # offset = request.GET.get('offset', 0)

    # oldest stories first
    stories = Story.objects \
                .select_related('data_source')[:limit]
    last_id = stories[limit-1].id
    
    return render(request, 'frontend/index.html', 
                  {'stories': stories,
                   'last_id': last_id})

def about(request):
    text_body = "foo"
    return render(request, 'frontend/index.html',
                  {'text_body': text_body})

def no_stories():
    """
    clears out the "load more" if there are no stories to load
    """
    return DatastarResponse(
                SSE.remove_elements("#load-more")
            )

def more(request):
    signals = read_signals(request)
    logger.error("signals is %r" % signals)

    if signals and ('lastId' in signals):
        lastId = signals['lastId']
        limit = 10

        stories = Story.objects.filter(id__gt=lastId)[:limit]

        if len(stories) == 0:
            return no_stories()
        else:
            rendered = render_to_string('frontend/stories.html',
                        {'stories': stories}, request=request)
            newLastId = stories[limit-1].id

            # not well documented, but you can just return an array
            # to DatastarResponse.
            return DatastarResponse(
                [
                SSE.patch_elements(rendered,
                                    selector="#stories",
                                    mode=ElementPatchMode.APPEND),
                # note: it's NOT kebab case for signals sent from server
                SSE.patch_signals(
                            {"lastId": newLastId }
                        )
                ]
            )
    else:
        return no_stories()

@require_http_methods(['POST'])
def vote(request, direction, story_id):
    # TODO: enforce POST only
    logger.info("entered vote")
    # get story for ID
    try:
        story_obj = Story.objects.get(id=story_id)
    except Story.DoesNotExist:
        raise Http404("story does not exist")

    # determine if vote exists, if not, register it
    # FIXME: replace these mock values with actual ones
    if direction == "up":
        story_obj.can_up = lambda: False
    if direction == "down":
        story_obj.can_down = lambda: False

    rendered = render_to_string("frontend/story_panel.html", 
                                {'story': story_obj}, request=request)
    return DatastarResponse(
        [
            SSE.patch_elements(rendered)
        ]
    )