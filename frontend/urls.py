from django.urls import path

from .views import index, join, vote

from django.views.generic import TemplateView

urlpatterns = [
     path("",  index.index, name="index"),
     path("more", index.more, name="more"),
     path("join", join.join, name="join"),
     path("about", index.about, name="about"),
     path("vote/<direction>/<int:story_id>", vote.vote),
]