from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Story

from datastar_py.django import (DatastarResponse, ServerSentEventGenerator,
                                read_signals)
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

def no_stories():
    """
    clears out the "load more" if there are no stories to load
    """
    return DatastarResponse(
                ServerSentEventGenerator.remove_elements("#load-more")
            )

def more(request):

    ## still getting datastar PATCH working right
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
                        {'stories': stories, 'request': request})
            newLastId = stories[limit-1].id

            # not well documented, but you can just return an array
            # to DatastarResponse.
            return DatastarResponse(
                [ServerSentEventGenerator.patch_elements(rendered,
                                                    selector="#stories",
                                                    mode=ElementPatchMode.APPEND),
                # note: it's NOT kebab case for signals sent from server
                ServerSentEventGenerator.patch_signals(
                            {"lastId": newLastId }
                        )
                ]
            )
    else:
        return no_stories()
