from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("more", views.more, name="more")
]
