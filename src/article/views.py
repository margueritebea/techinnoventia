from django.shortcuts import render, get_object_or_404
from .models import Article

def article_detail(request, slug):
    # On récupère l'article et on pré-charge les sections pour éviter de faire 10 requêtes SQL
    article = get_object_or_404(
        Article.objects.prefetch_related('sections', 'tags', 'author__profile'),
        slug=slug,
        status='published'
    )

    return render(request, 'article/detail.html', {'article': article})
