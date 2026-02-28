from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile_detail(request):
    profile = request.user.profile

    return render(
        request,
        "notas/profile/detail.html",
        {
            "profile": profile,
        },
    )
