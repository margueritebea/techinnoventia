from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import ArticleViewSet, CategoryViewSet, CommentViewSet, TagViewSet, ToggleLikeAPIView

app_name = 'article'

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'comments', CommentViewSet, basename='comment')



urlpatterns = [
    # Vues Templates (Pages HTML)
    path('detail/<slug:slug>/', views.article_detail, name='detail'),
    # path('articles/', views.ArticleListView.as_view(), name='list'),
    path('', views.ArticleListView.as_view(), name='list'),

    path('api/<slug:slug>/like/', ToggleLikeAPIView.as_view(), name='api_toggle_like'),


    # Gestion des articles (authentification requise)
    path('create/', views.article_create, name='create'),
    path('edit/<slug:slug>/', views.article_edit, name='edit'),
    path('delete/<slug:slug>/', views.article_delete, name='delete'),
    path('my-articles/', views.my_articles, name='my_articles'),
    # Vues API DRF
    path('api/', include(router.urls)),
]


