from django.conf import settings
from django.db import models


class Post(models.Model):
    topic = models.ForeignKey(
        'forum.Topic', on_delete=models.CASCADE, related_name='posts'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts'
    )
    content = models.TextField()
    is_solution = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['topic', 'created_at']),
        ]

    def __str__(self):
        return f'Post #{self.pk} by {self.author.username}'
