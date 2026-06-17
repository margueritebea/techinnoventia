from django.db import models
from django.shortcuts import get_object_or_404, render

from ..models import QATag, Question


def qa_list(request):
    questions = (
        Question.objects.filter(is_approved=True)
        .select_related('author', 'author__profile')
        .prefetch_related('tags')
        .annotate(
            _vote_score=models.Count('upvoters') - models.Count('downvoters'),
            _answers_count=models.Count('answers', filter=models.Q(answers__is_approved=True)),
        )
    )
    sort = request.GET.get('sort', 'recent')
    if sort == 'votes':
        questions = questions.order_by('-_vote_score', '-created_at')
    else:
        questions = questions.order_by('-created_at')

    tag_slug = request.GET.get('tag')
    if tag_slug:
        questions = questions.filter(tags__slug=tag_slug)

    tags = QATag.objects.all()
    return render(request, 'qa/list.html', {
        'questions': questions,
        'tags': tags,
        'current_sort': sort,
        'current_tag': tag_slug,
    })


def ask_question(request):
    return render(request, 'qa/ask.html')


def qa_detail(request, slug):
    question = get_object_or_404(
        Question.objects.select_related('author', 'author__profile').prefetch_related('tags', 'answers__author__profile'),
        slug=slug,
    )
    Question.objects.filter(pk=question.pk).update(views_count=models.F('views_count') + 1)
    return render(request, 'qa/detail.html', {'question': question})
