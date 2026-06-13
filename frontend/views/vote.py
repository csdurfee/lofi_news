from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.decorators.http import require_http_methods

from frontend.models import Story, Vote

from datastar_py.django import DatastarResponse
from datastar_py.django import ServerSentEventGenerator as SSE

import logging
logger = logging.getLogger(__name__)

@require_http_methods(['POST', 'PATCH'])
@login_required(login_url="/accounts/login")
def vote(request, direction, story_id):
    logger.debug("entered vote")
    try:
        story = Story.objects.get(id=story_id)
    except Story.DoesNotExist:
        raise Http404("story does not exist")

    votes = Vote.by_user_and_stories(user_id=request.user.id,
                                     story_ids=[story.id])

    if (request.method == "DELETE") and (direction == "delete"):
        votes[story_id].delete()


    if request.method == "POST":
        v = Vote(user=request.user, story=story)
    elif request.method == "PATCH":
        try:
            v = Vote.objects.get(user=request.user, story=story)
        except Vote.DoesNotExist:
            raise Http404("vote doesn't exist")

    if direction == "up":
        v.direction = Vote.Direction.UP
    elif direction == "down":
        v.direction = Vote.Direction.DOWN

    v.save()
    votes[story.id] = [v]

    # if (request.method=="PATCH"):
    #     # this means the user Un-saved the item from the save list... make it disappear
    #     return DatastarResponse([
    #         SSE.remove_elements(f"#story-{story.id}")
    #     ])
    # else:
    #     # rendered = render_to_string("frontend/story_panel.html",
    #     #                             {'story': story,
    #     #                             'votes_on_page': votes}, request=request)
    #     # return DatastarResponse(
    #     #     [
    #     #         SSE.patch_elements(rendered)
    #     #     ]
    #     # )

    # patch story out on ANY type of vote.
    return DatastarResponse([
            SSE.remove_elements(f"#story-{story.id}")
    ])