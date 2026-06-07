
from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

from datastar_py.django import (DatastarResponse, read_signals)
from datastar_py.django import ServerSentEventGenerator as SSE

@require_http_methods(['GET', 'POST'])
def settings(request):
    rendered = render_to_string("frontend/settings.html",
                                request=request)
    return DatastarResponse(
        [
            SSE.patch_elements(rendered)
        ]
    )