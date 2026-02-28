from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Landing pública
    path("", include("core.urls")),

    # Auth system
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),

    # Main app
    path("app/", include("notas.urls")),
]