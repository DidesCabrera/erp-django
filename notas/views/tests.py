from django.shortcuts import render
from notas.models import Meal, DailyPlan, Program

def test_forks(request):
    return render(request, 'notas/test_forks.html', {
        'meals': Meal.objects.all(),
        'dailyplans': DailyPlan.objects.all(),
        'programs': Program.objects.all(),
    })
