from django.db import models
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Podcast(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name='podcasts')
    image = models.ImageField(upload_to='podcast_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def view_count(self):
        return self.views.count()

    def __str__(self):
        return self.title

class Episode(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name='episodes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True) 
    audio_file = models.FileField(upload_to='episodes/')
    transcript = models.TextField(blank=True, null=True)
    ai_summary = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='episode_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def view_count(self):
        return self.views.count()

    def __str__(self):
        return self.title