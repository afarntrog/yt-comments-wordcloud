from django.contrib import admin
from .models import *
# Register your models here.

# https://stackoverflow.com/a/23660030
class YoutubeUrlAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)

admin.site.register(YoutubeUrl, YoutubeUrlAdmin)
# admin.site.register(YoutubeUrl)