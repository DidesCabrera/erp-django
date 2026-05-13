from django.shortcuts import render


def landing(request):
    return render(request, "core/landing.html")


def privacy(request):
    return render(request, "core/privacy.html")


def terms(request):
    return render(request, "core/terms.html")


def support(request):
    return render(request, "core/support.html")