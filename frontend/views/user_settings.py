
from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

from datastar_py.django import (DatastarResponse, read_signals)
from datastar_py.django import ServerSentEventGenerator as SSE

import logging
logger = logging.getLogger(__name__)

DEFAULT_IS_CHECKED = False

@require_http_methods(['GET', 'POST'])
def user_settings(request):
    if request.method == "POST":
        return doPost(request)
    else:
        return doGet(request)

def doPost(request):
    """
    persist user settings.
    """
    new_tabs = 0
    if 'new_tabs' in request.POST:
        logger.error(f"doPost: got new_tabs with value {request.POST['new_tabs']}")
        new_tabs = request.POST['new_tabs']

        if new_tabs == 'on':
            new_tabs = 1
        elif new_tabs == 'off':
            new_tabs = 0

    request.session['new_tabs'] = new_tabs
    return _render_and_return(request, new_tabs, patch_signal=True)

def _render_and_return(request, new_tabs, patch_signal=False):
    rendered = render_to_string("frontend/user_settings.html", request=request)
    
    responses = [
        SSE.patch_elements(rendered)
    ]
    # need to send the signal to update the frontend.
    if patch_signal:
        logger.error(f"patching signal so that _newTabs is {new_tabs}")
        new_signal = SSE.patch_signals(
            {"_newTabs": new_tabs}
        )
        responses.append(new_signal)


    return DatastarResponse(responses)

def doGet(request):
    logger.error("got request %r" % request.POST)


    new_tabs = DEFAULT_IS_CHECKED

    if 'new_tabs' in request.session:
        logger.error(f"using new_tabs setting from request.session: {request.session['new_tabs']}")
        new_tabs = request.session['new_tabs']

    return _render_and_return(request, new_tabs)
