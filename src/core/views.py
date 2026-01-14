from django.shortcuts import render
from django.db.models import Count, Q, Exists, OuterRef

from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone

from article.models import Article, Category

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
    total_tutos = Article.objects.filter(tags__name__iexact='tutoriel').count()
    
    data_stats = {
        'total_members': total_members,
        'total_articles': total_articles,
        'total_categories': total_categories,
        'total_tutos': Article.objects.filter(tags__name__iexact='tutoriel').count(),
        'online': 12, # Valeur simulée pour l'instant
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
    return render(request, "core/testindex.html", context=data)



# from django.shortcuts import render
# from datetime import datetime, timedelta
# from django.utils import timezone

# # Vos stats existantes
# stats = [
#     {'value': '850+', 'label': 'Membres'},
#     {'value': '120+', 'label': 'Articles'},
#     {'value': '45', 'label': 'Tutoriels'},
#     {'value': '12', 'label': 'Catégories'},
# ]

# # Mock data pour les articles
# articles = [
#     {
#         'title': 'Comment maîtriser Django REST Framework en 2025',
#         'slug': 'maitriser-django-rest-framework-2025',
#         'excerpt': 'Découvrez les dernières techniques pour créer des API performantes avec Django REST Framework. De l\'authentification JWT aux serializers avancés...',
#         'category': {'name': 'Django'},
#         'is_trending': True,
#         'published_at': datetime.now() - timedelta(days=2),
#         'author': {
#             'username': 'john_doe',
#             'get_full_name': 'John Doe',
#         },
#         'read_time': 12,
#         'likes_count': 245,
#         'comments_count': 34,
#     },
#     {
#         'title': 'Optimiser PostgreSQL pour vos applications Django',
#         'slug': 'optimiser-postgresql-django',
#         'excerpt': 'Apprenez à configurer PostgreSQL pour des performances optimales avec Django. Indexation, caching avec Redis et requêtes optimisées.',
#         'category': {'name': 'Base de données'},
#         'is_trending': False,
#         'published_at': datetime.now() - timedelta(days=5),
#         'author': {
#             'username': 'jane_smith',
#             'get_full_name': 'Jane Smith',
#         },
#         'read_time': 8,
#         'likes_count': 156,
#         'comments_count': 22,
#     },
#     {
#         'title': 'React 19 : Nouvelles fonctionnalités à connaître',
#         'slug': 'react-19-nouvelles-fonctionnalites',
#         'excerpt': 'React 19 arrive avec des améliorations majeures : Server Components, Actions et bien plus. Guide complet pour migrer votre projet.',
#         'category': {'name': 'React JS'},
#         'is_trending': True,
#         'published_at': datetime.now() - timedelta(days=1),
#         'author': {
#             'username': 'alex_martin',
#             'get_full_name': 'Alex Martin',
#         },
#         'read_time': 15,
#         'likes_count': 389,
#         'comments_count': 67,
#     },
#     {
#         'title': 'Déployer Django sur Fedora avec Apache et Redis',
#         'slug': 'deployer-django-fedora-apache-redis',
#         'excerpt': 'Tutoriel complet pour déployer votre application Django sur Fedora Linux avec Apache, PostgreSQL et Redis pour les tâches asynchrones.',
#         'category': {'name': 'Déploiement'},
#         'is_trending': False,
#         'published_at': datetime.now() - timedelta(days=7),
#         'author': {
#             'username': 'dev_guy',
#             'get_full_name': 'Developer Guinea',
#         },
#         'read_time': 18,
#         'likes_count': 89,
#         'comments_count': 15,
#     },
# ]

# categories = [
#     {'name': 'Django', 'count': 34},
#     {'name': 'React JS', 'count': 27},
#     {'name': 'Base de données', 'count': 19},
#     {'name': 'Déploiement', 'count': 12},
# ]


# users = [
#     {'username': 'MKalice_wonder', 'profile': {'role': 'Membre'}},
#     {'username': 'bob_builder', 'profile': {'role': 'Modérateur'}},
#     {'username': 'charlie_chaplin', 'profile': {'role': 'Administrateur'}},
#     {'username': 'diana_prince', 'profile': {'role': 'Membre'}},
# ]
# def home(request):
#     data = {
#         "stats": stats,
#         "articles": articles,
#         "categories": categories,
#         "active_users": users,
#     }
#     return render(request, "core/testindex.html", context=data)

