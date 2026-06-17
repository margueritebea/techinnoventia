from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Topic(models.Model):
    category = models.ForeignKey(
        'forum.Category', on_delete=models.CASCADE, related_name='topics'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_topics'
    )
    content = models.TextField(help_text='Premier message du sujet')
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'topics'
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['-is_pinned', '-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1
            while Topic.objects.filter(slug=slug).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def replies_count(self):
        return self.posts.filter(is_approved=True).count() - 1

    @property
    def last_post(self):
        return self.posts.filter(is_approved=True).order_by('-created_at').first()
