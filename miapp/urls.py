from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth system
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),

    # Main app
    path("", include("notas.urls")),
]
