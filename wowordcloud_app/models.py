from django.db import models

# Create your models here.
class YoutubeUrl(models.Model):
    yt_url = models.CharField(max_length=200)

    def __str__(self):
        return self.yt_url[:50]