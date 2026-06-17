from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.api_views import AnswerViewSet, QATagViewSet, QuestionViewSet
from .views.template_views import ask_question, qa_detail, qa_list

app_name = 'qa'

router = DefaultRouter()
router.register(r'tags', QATagViewSet, basename='tag')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'answers', AnswerViewSet, basename='answer')

urlpatterns = [
    path('', qa_list, name='list'),
    path('ask/', ask_question, name='ask'),
    path('<slug:slug>/', qa_detail, name='detail'),
    path('api/', include(router.urls)),
]
