from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView

google_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)

def signup_view(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login después de registrarse
            return redirect("dailyplan_list")  # o donde quieras

    return render(request, "auth/signup.html", {"form": form})

google_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)