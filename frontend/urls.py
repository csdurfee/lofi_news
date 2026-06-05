from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("more", views.more, name="more"),
    path("join", views.join, name="join"),
    path("vote/<direction>/<int:story_id>", views.vote),
]
