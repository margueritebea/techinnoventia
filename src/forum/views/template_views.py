from django.db import models
from django.shortcuts import get_object_or_404, render

from ..models import Category, Topic


def forum_list(request):
    categories = (
        Category.objects.filter(is_active=True)
        .prefetch_related(
            models.Prefetch(
                'topics',
                queryset=Topic.objects.filter(is_approved=True)
                .select_related('author')
                .annotate(replies_count=models.Count('posts', filter=models.Q(posts__is_approved=True)))
                .order_by('-is_pinned', '-created_at')[:5],
            )
        )
        .annotate(topics_count=models.Count('topics', filter=models.Q(topics__is_approved=True)))
    )
    return render(request, 'forum/list.html', {'categories': categories})


def topic_create(request):
    return render(request, 'forum/create.html')


def topic_detail(request, slug):
    topic = get_object_or_404(
        Topic.objects.select_related('author', 'author__profile', 'category'),
        slug=slug,
    )
    Topic.objects.filter(pk=topic.pk).update(views_count=models.F('views_count') + 1)
    return render(request, 'forum/detail.html', {'topic': topic})
