# authentication/urls.py
from django.urls import path #, include
from . import views

app_name = "authentication"

urlpatterns = [
    path('signin/', views.login_page, name='login'),
    path('signup/', views.login_page, name='register'),

    # API DRF
    path("api/register/", views.RegisterView.as_view(), name="api_register"),
    path("api/check-auth/", views.check_auth, name="check-auth"),
    path("api/login/", views.LoginView.as_view(), name="api_login"),
    path("api/logout/", views.LogoutView.as_view(), name="api_logout"),
    path("api/token/refresh/", views.CookieTokenRefreshView.as_view(), name="api_token_refresh"),    
]
