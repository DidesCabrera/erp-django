from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

def root_redirect(request):
    return redirect("/accounts/login/")

urlpatterns = [
    path("", root_redirect),
    path("admin/", admin.site.urls),

    # Auth system
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),

    # Main app
    path("", include("notas.urls")),
]
