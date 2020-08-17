from django.db import models
from django.conf import settings
from posts.models import Post
from django.utils.timezone import now


# Create your models here.

class Comment(models.Model):
    body = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    last_mod = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.body