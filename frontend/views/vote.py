from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods

from ..models import Story, Vote

from datastar_py.django import (DatastarResponse, read_signals)
from datastar_py.django import ServerSentEventGenerator as SSE

import logging
logger = logging.getLogger(__name__)

# FIXME: this is going to an unstyled page right now (I think it's datastar's fault)
@login_required(login_url="/accounts/login")
@require_http_methods(['POST'])
def vote(request, direction, story_id):
    logger.debug("entered vote")
    try:
        story = Story.objects.get(id=story_id)
    except Story.DoesNotExist:
        raise Http404("story does not exist")
    
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
        votes[story.id] = [v]

    rendered = render_to_string("frontend/story_panel.html", 
                                {'story': story,
                                 'votes_on_page': votes}, request=request)
    return DatastarResponse(
        [
            SSE.patch_elements(rendered)
        ]
    )