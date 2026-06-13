from django.contrib import admin

# Register your models here.

from .models import Story, DataSource, Vote, Channel

admin.site.register([Story, DataSource, Vote, Channel])
