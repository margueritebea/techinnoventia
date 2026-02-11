# authentication/urls.py
from django.urls import path #, include
from . import views

app_name = "authentication"

urlpatterns = [
    path('signin/', views.login_page, name='login'),
    path('signup/', views.register_page, name='register'),

    # API DRF
    path("api/register/", views.RegisterView.as_view(), name="api_register"),
    path("api/check-auth/", views.check_auth, name="check-auth"),
    path("api/login/", views.LoginView.as_view(), name="api_login"),
    path("api/logout/", views.LogoutView.as_view(), name="api_logout"),
    path("api/token/refresh/", views.CookieTokenRefreshView.as_view(), name="api_token_refresh"),    

    # Profile URLs
    path('profile/', views.profile_page, name='profile-page'),  # Mon profil
    path('profile/<str:username>/', views.profile_page, name='profile-page-user'),  # Profil public
    
    path('api/profile/me/', views.current_user_profile, name='current-user-profile'),
    path('api/profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('api/profile/me/avatar/', views.upload_avatar, name='upload-avatar'),
    path('api/profile/me/cover/', views.upload_cover, name='upload-cover'),
    path('api/profile/<str:username>/stats/', views.user_stats, name='user-stats'),
]



