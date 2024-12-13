from django.db import models
from users.models import User
from podcasts.models import Episode, Podcast

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user} on {self.podcast}"

class View(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, null=True, blank=True, related_name='views')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True, blank=True, related_name='views')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['podcast']),
            models.Index(fields=['episode']),
        ]

    def __str__(self):
        content = self.podcast if self.podcast else self.episode
        return f"View by {self.user or 'Anonymous'} on {content}"