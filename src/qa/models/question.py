from django.conf import settings
from django.db import models
from django.utils.text import slugify


class QATag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Question(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions'
    )
    tags = models.ManyToManyField(QATag, blank=True, related_name='questions')
    upvoters = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='question_upvotes'
    )
    downvoters = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='question_downvotes'
    )
    views_count = models.PositiveIntegerField(default=0)
    is_resolved = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['-views_count']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1
            while Question.objects.filter(slug=slug).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def vote_score(self):
        return self.upvoters.count() - self.downvoters.count()

    @property
    def answers_count(self):
        return self.answers.filter(is_approved=True).count()
