from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup_view(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login después de registrarse
            return redirect("dailyplan_list")  # o donde quieras

    return render(request, "accounts/signup.html", {"form": form})
