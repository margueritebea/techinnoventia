from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.api_views import CategoryViewSet, TopicViewSet
from .views.template_views import forum_list, topic_create, topic_detail

app_name = 'forum'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'topics', TopicViewSet, basename='topic')

urlpatterns = [
    path('', forum_list, name='list'),
    path('create/', topic_create, name='create'),
    path('<slug:slug>/', topic_detail, name='detail'),
    path('api/', include(router.urls)),
]
