from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string

from frontend.models import Story


@login_required(login_url="/accounts/login")
def saved(request):
    saved_stories = Story.saved(request.user.id)

    # FIXME: have an 'unsave' button or hide the save button
    rendered = render_to_string('frontend/index.html',
        {
            'stories': saved_stories,
            'saved_view': True
        }, request=request
    )
    return HttpResponse(rendered)

# def _return_json(saved_stories):
#     data = [
#         {
#             'id': s.id,
#             'title': s.title,
#             'url': s.original_url,
#             'source': s.data_source.code,
#             'retrieved': s.retrieved.isoformat(),
#         }
#         for s in saved_stories
#     ]
#     return JsonResponse(data, safe=False,
#                         json_dumps_params={'indent': 2})
