from django.contrib import admin
from .models import Podcast, Episode, Category

admin.site.register(Podcast)
admin.site.register(Episode)
admin.site.register(Category)