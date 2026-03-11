"""Root URL configuration for django-auth-basic."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("apps.authentication.urls", namespace="authentication")),
    path("account/", include("apps.profiles.urls", namespace="profiles")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
