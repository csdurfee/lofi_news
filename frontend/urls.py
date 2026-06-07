from django.urls import path

from .views import index, join, user_settings, vote

urlpatterns = [
     path("",  index.index, name="index"),
     path("more", index.more, name="more"),
     path("join", join.join, name="join"),
     path("settings", user_settings.user_settings, name="settings"),
     path("about", index.about, name="about"),
     path("vote/<direction>/<int:story_id>", vote.vote),
]