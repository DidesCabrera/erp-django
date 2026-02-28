from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include


urlpatterns = [
    path("", lambda request: redirect("accounts/login/")),
    
    path("admin/", admin.site.urls),
    
    # Landing pública
    path("", include("core.urls")),

    # Auth system
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),

    # Main app
    path("", include("notas.urls")),
]