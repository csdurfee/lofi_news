
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
    if 'newTabs' in request.POST:
        logger.error(f"doPost: got newTabs with value {request.POST['newTabs']}")
        newTabs = request.POST['newTabs']
        # FIXME: I need to deal with 'on', 'off' hewrerere
        if newTabs == 'on':
            newTabs = 1
        else:
            newTabs = 0
    else:
        logger.error("doPost: newTabs off")
        newTabs = 0
    request.session['newTabs'] = newTabs
    return _render_and_return(request, newTabs, patch_signal=True)

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

    signals = read_signals(request)
    
    # TODO: factor this newTabs logic out
    #  and write some tests for this.

    # if newTabs signal comes in, it wins, and we update the session
    newTabs = DEFAULT_IS_CHECKED
    if signals and ('newTabs' in signals):
        request.session['newTabs'] = signals['newTabs']
        logger.error(f"signals: setting newTabs to {signals['newTabs']}")
        newTabs = signals['newTabs']
    # otherwise, we use the session's newTabs setting
    if 'newTabs' in request.session:
        logger.error(f"using newTabs setting from request.session: {request.session['newTabs']}")
        newTabs = request.session['newTabs']

    return _render_and_return(request, newTabs)
