
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

    rendered = render_to_string("frontend/user_settings.html", 
                                {"new_tabs": newTabs},
                                request=request)
    return DatastarResponse(
        [
            SSE.patch_elements(rendered)
        ]
    )