from django.urls import path

from .views import index, join, user_settings, vote

urlpatterns = [
     path("",  index.index, name="index"),
     
     path("more/<source_code>", index.more, name="source_more"),
     path("more", index.more, name="more"),

     path("about", index.about, name="about"),
     path("source/<source_code>", index.index, name="source"),

     path("join", join.join, name="join"),
     path("settings", user_settings.user_settings, name="settings"),
     path("vote/<direction>/<int:story_id>", vote.vote),
]