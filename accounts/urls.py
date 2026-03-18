from django.urls import path
from . import views
from .views import google_login


urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("google/", google_login, name="google_login"),
]