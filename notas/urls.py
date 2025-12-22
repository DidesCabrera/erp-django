from django.urls import path
from .views.meals import (
    fork_meal, 
    replace_meal, 
    copy_meal, 
    meal_detail, 
    meal_list, 
    meal_create, 
    add_food_to_meal,
    configure_meal
)
from .views.dailyplans import (
    fork_dailyplan,
    copy_dailyplan,
    dailyplan_detail,
    dailyplan_list,
    dailyplan_create,
    add_meal_to_dailyplan,
    configure_dailyplan,
    remove_meal
)
from .views.programs import (
    fork_program,
    copy_program,
    program_detail,
    program_list,
    program_create,
    add_dailyplan_to_program,
    configure_program
)
from .views.foods import import_foods, download_food_template, food_list
from .views.tests import test_forks

urlpatterns = [

    #MEALS
    path("meals/", meal_list, name="meal_list"),
    path("meals/create/", meal_create, name="meal_create"),
    path("meals/<int:pk>/configure/", configure_meal, name="configure_meal"),
    path("meals/<int:pk>/add-food/", add_food_to_meal, name="add_food_to_meal"),
    path("meals/<int:pk>/", meal_detail, name="meal_detail"),
    path('meals/<int:meal_id>/fork/', fork_meal, name='fork_meal'),
    path("meals/<int:pk>/copy/", copy_meal, name="copy_meal"),

    path('daily-plan-meals/<int:daily_plan_meal_id>/replace/<int:new_meal_id>/', replace_meal, name='replace_meal'),

    #DAILY PLANS
    path("dailyplans/", dailyplan_list, name="dailyplan_list"),
    path("dailyplans/create/", dailyplan_create, name="dailyplan_create"),
    path("dailyplans/<int:pk>/configure/", configure_dailyplan, name="configure_dailyplan"),
    path("dailyplans/<int:pk>/add-meal/", add_meal_to_dailyplan, name="add_meal_to_dailyplan"),
    path("dailyplans/<int:pk>/", dailyplan_detail, name="dailyplan_detail"), 
    path('dailyplans/<int:dailyplan_id>/fork/', fork_dailyplan, name='fork_dailyplan'),
    path("dailyplans/<int:pk>/copy/", copy_dailyplan, name="copy_dailyplan"),
    
    path("dailyplans/<int:dailyplan_id>/meals/<int:item_id>/remove/", remove_meal, name="remove_meal"),
    path("dailyplans/<int:dailyplan_id>/meals/<int:pk>/", meal_detail, name="dailyplan_meal_detail"),  
    
    #PROGRAMS
    path("programs/", program_list, name="program_list"),
    path("programs/create/", program_create, name="program_create"),
    path("programs/<int:pk>/configure/", configure_program, name="configure_program"),
    path("programs/<int:pk>/add-dailyplan/", add_dailyplan_to_program, name="add_dailyplan_to_program"),
    path("programs/<int:pk>/", program_detail, name="program_detail"),
    path('programs/<int:program_id>/fork/', fork_program, name='fork_program'),
    path("programs/<int:pk>/copy/", copy_program, name="copy_program"),
    
    #FOODS
    path("foods/import/", import_foods, name="import_foods"),
    path("foods/template/", download_food_template, name="download_food_template"),
    path("foods/", food_list, name="food_list"),



    path('test-forks/', test_forks, name='test_forks')
    
]
