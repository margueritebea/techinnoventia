from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import render
from django.utils import timezone

from article.models import Article, Category
from forum.models import Post, Topic
from qa.models import Answer, Question

User = get_user_model()

def home(request):
    # 1. Récupérer les articles publiés
    articles_qs = Article.objects.filter(status='published').select_related('author', 'category', 'author__profile').prefetch_related('tags', 'likes')
    # articles_qs = Article.objects.filter(status='published').select_related('author', 'category')

    # Optimisation: On ajoute un champ booléen 'is_liked_by_user' à chaque article
    if request.user.is_authenticated:
        articles_qs = articles_qs.annotate(
            is_liked_by_user=Exists(
                Article.likes.through.objects.filter(
                    article_id=OuterRef('pk'),
                    user_id=request.user.id
                )
            )
        )
    # Articles récents (limite à 6)
    recent_articles = articles_qs.order_by('-published_at')[:6]

    # 2. Statistiques dynamiques
    total_members = User.objects.count()
    total_articles = Article.objects.filter(status='published').count()
    total_categories = Category.objects.count()
    # Exemple statique pour "tutoriels" si tu n'as pas de type spécifique
    Article.objects.filter(tags__name__iexact='tutoriel').count()

    data_stats = {
        'total_members': total_members,
        'total_articles': total_articles,
        'total_categories': total_categories,
        'total_tutos': Article.objects.filter(tags__name__iexact='tutoriel').count(),
        'online': User.objects.filter(last_login__gte=timezone.now() - timedelta(minutes=15)).count(),
        'new_articles': Article.objects.filter(status='published', created_at__date=timezone.now().date()).count()
    }


    # 3. Catégories avec le nombre d'articles (Annotation)
    categories_list = Category.objects.annotate(
        count=Count('articles', filter=Q(articles__status='published'))
    ).order_by('-count')[:5]

    # 4. Utilisateurs actifs (Exemple: les 5 derniers inscrits ou connectés)
    # Idéalement, on filtre sur is_active=True
    active_users = User.objects.filter(is_active=True).select_related('profile').order_by('-date_joined')[:5]

    data = {
        "stats": data_stats, # On passe le dictionnaire ici
        "articles": recent_articles,
        "categories": categories_list,
        "active_users": active_users,
    }
    return render(request, "core/index.html", context=data)


def search(request):
    query = request.GET.get('q', '').strip()
    results = {'articles': [], 'topics': [], 'questions': [], 'query': query}

    if query and len(query) >= 2:
        results['articles'] = (
            Article.objects.filter(status='published')
            .filter(Q(title__icontains=query) | Q(excerpt__icontains=query))
            .select_related('author', 'category')
            .distinct()[:5]
        )
        results['topics'] = (
            Topic.objects.filter(is_approved=True)
            .filter(Q(title__icontains=query) | Q(content__icontains=query))
            .select_related('author', 'category')
            .distinct()[:5]
        )
        results['posts'] = (
            Post.objects.filter(is_approved=True, content__icontains=query)
            .select_related('author', 'topic')
            .distinct()[:5]
        )
        results['questions'] = (
            Question.objects.filter(is_approved=True)
            .filter(Q(title__icontains=query) | Q(content__icontains=query))
            .select_related('author')
            .distinct()[:5]
        )
        results['answers'] = (
            Answer.objects.filter(is_approved=True, content__icontains=query)
            .select_related('author', 'question')
            .distinct()[:5]
        )
    return render(request, 'core/search.html', results)

