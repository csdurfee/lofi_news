from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string

from frontend.models import Story

@login_required(login_url="/accounts/login")
def saved(request):
    saved_stories = Story.saved(request.user.id)

    rendered = render_to_string('frontend/index.html',
        {
            'stories': saved_stories,
            'saved_view': True
        }, request=request
    )
    return HttpResponse(rendered)