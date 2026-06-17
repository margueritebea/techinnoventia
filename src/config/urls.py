from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [path('authorized-admin/', admin.site.urls), path('', include('core.urls')), path('users/', include('authentication.urls')),     path('article/', include('article.urls')),
    path('forum/', include('forum.urls')),
    path('qa/', include('qa.urls')),
    path('api-auth/', include('rest_framework.urls')), path('ia_chat/', include('ia_chat.urls')), *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
