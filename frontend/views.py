from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import UserCreationForm
from django.http import Http404, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods

from .models import Story, Vote

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
    story_ids = {story.id for story in stories}

    # grab related votes
    if request.user:
        votes_on_page = Vote.by_user_and_stories(request.user.id, story_ids)
    else:
        votes_on_page = {}
    return render(request, 'frontend/index.html', 
                  {'stories': stories,
                   'votes_on_page': votes_on_page,
                   'last_id': last_id})

def about(request):
    text_body = "this page left intentionally blank"
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

# FIXME: this is going to an unstyled page
@login_required(login_url="/accounts/login")
@require_http_methods(['POST'])
def vote(request, direction, story_id):
    logger.info("entered vote")
    # get story for ID
    try:
        story = Story.objects.get(id=story_id)
    except Story.DoesNotExist:
        raise Http404("story does not exist")
    
    # TODO: this should be a transaction block
    votes = Vote.by_user_and_stories(user_id=request.user.id, 
                                     story_ids=[story.id])
    if story_id in votes:
        return HttpResponseBadRequest("already voted, no take backsies")

    if direction == "up":
        v = Vote(user=request.user, story=story, direction = 1)
        v.save()
        votes[story.id] = [v]

    if direction == "down":
        v = Vote(user=request.user, story=story, direction = -1)
        v.save()
        votes[story.id] = v

    rendered = render_to_string("frontend/story_panel.html", 
                                {'story': story,
                                 'votes_on_page': votes}, request=request)
    return DatastarResponse(
        [
            SSE.patch_elements(rendered)
        ]
    )