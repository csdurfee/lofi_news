from django.shortcuts import render
from .models import Story


def index(request):
    stories = Story.objects.select_related('data_source').order_by('-retrieved')
    return render(request, 'frontend/index.html', {'stories': stories})