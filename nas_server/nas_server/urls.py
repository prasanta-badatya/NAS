from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        "name": "Private NAS API",
        "version": "1.0",
        "endpoints": {
            "auth": "/api/auth/",
            "media": "/api/media/",
            "admin": "/admin/",
        }
    })


urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/media/", include("media_manager.urls")),
]
