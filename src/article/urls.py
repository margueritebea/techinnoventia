from django.urls import path
from . import views
from . import api_views # On importe nos vues API

app_name = 'article'

urlpatterns = [
    # Vues Templates (Pages HTML)
    path('detail/<slug:slug>/', views.article_detail, name='detail'),

    # Endpoints API (JSON)
    path('api/<slug:slug>/like/', api_views.ToggleLikeAPIView.as_view(), name='api_toggle_like'),
]
