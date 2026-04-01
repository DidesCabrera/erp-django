from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def project_view(request):
    
    return render(
        request,
        "notas/project.html"
    )
