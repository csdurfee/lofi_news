from django.shortcuts import render
from .models import Story

import logging
logger = logging.getLogger(__name__)

def index(request):
    #logger.error("hoo boy")
    stories = Story.objects.select_related('data_source').order_by('-retrieved')
    return render(request, 'frontend/index.html', {'stories': stories})