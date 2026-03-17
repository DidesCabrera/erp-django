from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Landing pública
    path("", include("core.urls")),

    # Auth system
    path("auth/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),

    # Main app
    path("app/", include("notas.urls")),
]

