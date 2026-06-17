from django.conf import settings
from django.db import models


class Answer(models.Model):
    question = models.ForeignKey(
        'qa.Question', on_delete=models.CASCADE, related_name='answers'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers'
    )
    content = models.TextField()
    is_accepted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    upvoters = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='answer_upvotes'
    )
    downvoters = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='answer_downvotes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_accepted', 'created_at']
        indexes = [
            models.Index(fields=['question', 'created_at']),
        ]

    def __str__(self):
        return f'Answer #{self.pk} by {self.author.username}'

    @property
    def vote_score(self):
        return self.upvoters.count() - self.downvoters.count()
