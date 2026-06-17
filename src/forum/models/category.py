from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Emoji ou icône (ex: 💻)')
    color = models.CharField(max_length=7, blank=True, help_text='Couleur hex (ex: #3B82F6)')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def topics_count(self):
        return self.topics.count()

    @property
    def posts_count(self):
        from django.db.models import Count, Q

        from .topic import Topic
        return Topic.objects.filter(category=self).aggregate(
            total=Count('posts', filter=Q(posts__is_approved=True))
        )['total'] or 0
