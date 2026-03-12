"""Root URL configuration for django-auth-basic."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import include, path


def health_check(request: HttpRequest) -> JsonResponse:
    """Lightweight health check for container orchestration probes."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path("auth/", include("apps.authentication.urls", namespace="authentication")),
    path("account/", include("apps.profiles.urls", namespace="profiles")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
