from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db.models import Count, Q
from .models import Article, Category, Tag
from django.contrib.auth import get_user_model

User = get_user_model()


# ========== VUES POUR L'AFFICHAGE ==========

def article_detail(request, slug):
    """Vue de détail d'un article"""
    article = get_object_or_404(
        Article.objects.prefetch_related('sections', 'tags', 'author__profile'),
        slug=slug,
        status='published'
    )
    return render(request, 'article/detail.html', {'article': article})


class ArticleListView(ListView):
    """Vue pour afficher la liste des articles publiés"""
    model = Article
    template_name = 'article/list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = Article.objects.filter(
            status='published'
        ).select_related(
            'author',
            'category'
        ).prefetch_related(
            'tags',
            'sections',
            'likes',
            'comments'
        ).order_by('-published_at')

        # Filtrage par catégorie
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filtrage par tag
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        # Recherche
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(sections__content__icontains=search_query)
            ).distinct()

        # Tri
        sort = self.request.GET.get('sort', 'recent')
        if sort == 'popular':
            queryset = queryset.annotate(
                likes_total=Count('likes')
            ).order_by('-likes_total', '-published_at')
        elif sort == 'trending':
            queryset = queryset.filter(is_trending=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.annotate(
            article_count=Count('articles', filter=Q(articles__status='published'))
        ).filter(article_count__gt=0)

        context['popular_tags'] = Tag.objects.annotate(
            article_count=Count('article', filter=Q(article__status='published'))
        ).filter(article_count__gt=0).order_by('-article_count')[:10]

        context['trending_articles'] = Article.objects.filter(
            status='published',
            is_trending=True
        ).select_related('author', 'category')[:5]

        context['active_authors'] = User.objects.annotate(
            article_count=Count('articles', filter=Q(articles__status='published'))
        ).filter(article_count__gt=0).order_by('-article_count')[:5]

        context['total_articles'] = Article.objects.filter(status='published').count()
        context['total_authors'] = User.objects.filter(articles__status='published').distinct().count()
        context['total_categories'] = Category.objects.filter(articles__status='published').distinct().count()

        context['current_category'] = self.request.GET.get('category', '')
        context['current_tag'] = self.request.GET.get('tag', '')
        context['current_sort'] = self.request.GET.get('sort', 'recent')
        context['search_query'] = self.request.GET.get('q', '')

        return context


# ========== VUES POUR L'ÉDITION ==========

@login_required
def article_create(request):
    """Vue pour créer un nouvel article"""
    return render(request, 'article/article_create.html')


@login_required
def article_edit(request, slug):
    """Vue pour éditer un article existant"""
    article = get_object_or_404(Article, slug=slug, author=request.user)
    return render(request, 'article/article_create.html', {'article': article})


@login_required
def my_articles(request):
    """Liste des articles de l'utilisateur connecté"""
    articles = Article.objects.filter(
        author=request.user
    ).select_related('category').prefetch_related('tags', 'likes').order_by('-created_at')
    
    # Calcul des statistiques
    stats = {
        'total': articles.count(),
        'published': articles.filter(status='published').count(),
        'draft': articles.filter(status='draft').count(),
        'total_likes': sum(article.likes_count for article in articles),
    }
    
    return render(request, 'article/my_articles.html', {
        'articles': articles,
        'stats': stats
    })


@login_required
def article_delete(request, slug):
    """Supprimer un article"""
    article = get_object_or_404(Article, slug=slug, author=request.user)
    
    if request.method == 'POST':
        article.delete()
        return redirect('article:my_articles')
    
    return render(request, 'article/delete_confirm.html', {'article': article})
# from django.shortcuts import render, get_object_or_404
# from .models import Article


# from django.shortcuts import render
# from django.views.generic import ListView
# from django.db.models import Count, Q
# from .models import Article, Category, Tag
# from django.contrib.auth import get_user_model

# User = get_user_model()

# def article_detail(request, slug):
#     # On récupère l'article et on pré-charge les sections pour éviter de faire 10 requêtes SQL
#     article = get_object_or_404(
#         Article.objects.prefetch_related('sections', 'tags', 'author__profile'),
#         slug=slug,
#         status='published'
#     )

#     return render(request, 'article/detail.html', {'article': article})


# class ArticleListView(ListView):
#     """
#     Vue pour afficher la liste des articles publiés
#     """
#     model = Article
#     template_name = 'article/list.html'
#     context_object_name = 'articles'
#     paginate_by = 10

#     def get_queryset(self):
#         """
#         Retourne uniquement les articles publiés, avec leurs relations
#         """
#         queryset = Article.objects.filter(
#             status='published'
#         ).select_related(
#             'author',
#             'category'
#         ).prefetch_related(
#             'tags',
#             'sections',
#             'likes',
#             'comments'  # Ajout pour optimiser comments_count
#         ).order_by('-published_at')

#         # Filtrage par catégorie
#         category_slug = self.request.GET.get('category')
#         if category_slug:
#             queryset = queryset.filter(category__slug=category_slug)

#         # Filtrage par tag
#         tag_slug = self.request.GET.get('tag')
#         if tag_slug:
#             queryset = queryset.filter(tags__slug=tag_slug)

#         # Recherche
#         search_query = self.request.GET.get('q')
#         if search_query:
#             queryset = queryset.filter(
#                 Q(title__icontains=search_query) |
#                 Q(excerpt__icontains=search_query) |
#                 Q(sections__content__icontains=search_query)
#             ).distinct()

#         # Tri
#         sort = self.request.GET.get('sort', 'recent')
#         if sort == 'popular':
#             queryset = queryset.annotate(
#                 likes_total=Count('likes')
#             ).order_by('-likes_total', '-published_at')
#         elif sort == 'trending':
#             queryset = queryset.filter(is_trending=True)

#         return queryset

#     def get_context_data(self, **kwargs):
#         """
#         Ajoute des données supplémentaires au contexte
#         """
#         context = super().get_context_data(**kwargs)

#         # Catégories avec nombre d'articles
#         context['categories'] = Category.objects.annotate(
#             article_count=Count('articles', filter=Q(articles__status='published'))
#         ).filter(article_count__gt=0)

#         # Tags populaires
#         context['popular_tags'] = Tag.objects.annotate(
#             article_count=Count('article', filter=Q(article__status='published'))
#         ).filter(article_count__gt=0).order_by('-article_count')[:10]

#         # Articles tendance (sidebar)
#         context['trending_articles'] = Article.objects.filter(
#             status='published',
#             is_trending=True
#         ).select_related('author', 'category')[:5]

#         # Auteurs actifs (pour sidebar)
#         context['active_authors'] = User.objects.annotate(
#             article_count=Count('articles', filter=Q(articles__status='published'))
#         ).filter(article_count__gt=0).order_by('-article_count')[:5]

#         # Statistiques globales
#         context['total_articles'] = Article.objects.filter(status='published').count()
#         context['total_authors'] = User.objects.filter(articles__status='published').distinct().count()
#         context['total_categories'] = Category.objects.filter(articles__status='published').distinct().count()

#         # Paramètres de filtrage actuels
#         context['current_category'] = self.request.GET.get('category', '')
#         context['current_tag'] = self.request.GET.get('tag', '')
#         context['current_sort'] = self.request.GET.get('sort', 'recent')
#         context['search_query'] = self.request.GET.get('q', '')

#         return context


# # Vue fonction alternative (plus simple)
# def article_list(request):
#     """
#     Vue fonction pour afficher la liste des articles
#     """
#     # Récupération des articles publiés
#     articles = Article.objects.filter(
#         status='published'
#     ).select_related(
#         'author',
#         'category'
#     ).prefetch_related(
#         'tags',
#         'sections',
#         'likes',
#         'comments'  # Ajout pour optimiser comments_count
#     ).order_by('-published_at')

#     # Filtres
#     category_slug = request.GET.get('category')
#     if category_slug:
#         articles = articles.filter(category__slug=category_slug)

#     tag_slug = request.GET.get('tag')
#     if tag_slug:
#         articles = articles.filter(tags__slug=tag_slug)

#     search_query = request.GET.get('q')
#     if search_query:
#         articles = articles.filter(
#             Q(title__icontains=search_query) |
#             Q(excerpt__icontains=search_query)
#         ).distinct()

#     # Tri
#     sort = request.GET.get('sort', 'recent')
#     if sort == 'popular':
#         articles = articles.annotate(likes_total=Count('likes')).order_by('-likes_total')

#     # Données du contexte
#     context = {
#         'articles': articles[:10],  # Limiter à 10 articles
#         'categories': Category.objects.annotate(
#             article_count=Count('articles', filter=Q(articles__status='published'))
#         ).filter(article_count__gt=0),
#         'popular_tags': Tag.objects.annotate(
#             article_count=Count('article', filter=Q(article__status='published'))
#         ).filter(article_count__gt=0).order_by('-article_count')[:10],
#         'trending_articles': Article.objects.filter(
#             status='published', 
#             is_trending=True
#         ).select_related('author', 'category')[:5],
#         'active_authors': User.objects.annotate(
#             article_count=Count('articles', filter=Q(articles__status='published'))
#         ).filter(article_count__gt=0).order_by('-article_count')[:5],
#         'total_articles': Article.objects.filter(status='published').count(),
#         'total_authors': User.objects.filter(articles__status='published').distinct().count(),
#         'total_categories': Category.objects.filter(articles__status='published').distinct().count(),
#         'current_sort': sort,
#         'current_category': category_slug or '',
#         'current_tag': tag_slug or '',
#         'search_query': search_query or '',
#     }

#     return render(request, 'articles/list.html', context)

# ###################################################################################################

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.views.generic import ListView
# from django.db.models import Count, Q
# from .models import Article, Category, Tag
# from django.contrib.auth import get_user_model

# User = get_user_model()


# # ========== VUES POUR L'AFFICHAGE ==========

# def article_detail(request, slug):
#     """Vue de détail d'un article"""
#     article = get_object_or_404(
#         Article.objects.prefetch_related('sections', 'tags', 'author__profile'),
#         slug=slug,
#         status='published'
#     )
#     return render(request, 'article/detail.html', {'article': article})



# # ========== VUES POUR L'ÉDITION ==========

# @login_required
# def article_create(request):
#     """Vue pour créer un nouvel article"""
#     return render(request, 'article/article_create.html')


# @login_required
# def article_edit(request, slug):
#     """Vue pour éditer un article existant"""
#     article = get_object_or_404(Article, slug=slug, author=request.user)
#     return render(request, 'article/article_create.html', {'article': article})


# @login_required
# def my_articles(request):
#     """Liste des articles de l'utilisateur connecté"""
#     articles = Article.objects.filter(
#         author=request.user
#     ).select_related('category').prefetch_related('tags', 'likes').order_by('-created_at')
    
#     return render(request, 'article/my_articles.html', {'articles': articles})


# @login_required
# def article_delete(request, slug):
#     """Supprimer un article"""
#     article = get_object_or_404(Article, slug=slug, author=request.user)
    
#     if request.method == 'POST':
#         article.delete()
#         return redirect('article:my_articles')
    
#     return render(request, 'article/delete_confirm.html', {'article': article})
