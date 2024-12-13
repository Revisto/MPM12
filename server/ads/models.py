from django.db import models

class Ad(models.Model):
    audio_file = models.FileField(upload_to='ads/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)