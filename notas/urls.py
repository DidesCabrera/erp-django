from django.urls import path
from notas.interface.views.foods import (
    food_list,
    food_detail,
    food_create,
    food_edit,
    foods_json,
    import_foods, 
    download_food_template
)

from notas.interface.views.meals import (
    meal_fork,  
    meal_copy, 
    meal_detail, 
    meal_list, 
    meal_create,
    meal_configure,
    meal_rename,
    meal_explore_list,
    meal_explore_detail,
    meal_draft_list,
    meal_shared_list,
    meal_remove,
    meal_unshare,
    meal_draft_delete,
    meal_share,
    meal_share_accept,
    meal_share_dismiss,
    meal_share_detail,
)

from notas.interface.views.meal_foods import (
    mealfood_remove,
    mealfood_update,
    add_food_to_meal,
    mealfood_reorder,
)

from notas.interface.views.dailyplans import (
    dailyplan_fork,
    dailyplan_copy,
    dailyplan_detail,
    dailyplan_list,
    dailyplan_create,
    add_meal_from_list,
    dailyplan_configure,
    dailyplan_rename,
    dailyplan_explore_list,
    dailyplan_explore_detail, 
    create_meal_for_dailyplan,
    attach_meal_to_dailyplan,
    dailyplan_share,
    dailyplan_share_accept,
    dailyplan_share_dismiss,
    dailyplan_shared_list,
    dailyplan_remove,
    dailyplan_save,
    dailyplan_unshare,
    dailyplan_draft_list,
    dailyplan_draft_detail,
    dailyplan_draft_edit,
    dailyplan_shared_detail,
)



from notas.interface.views.dailyplan_meals import (
    dailyplan_meal_detail, 
    dailyplan_meal_edit, 
    dailyplan_add_meal,
    replace_dailyplan_meal,
    confirm_replace_meal,
    replace_meal,
    dailyplanmeal_remove,
    dailyplanmeal_update,
    dailyplanmeal_create_meal,
    dailyplanmeal_reorder,
)

from notas.interface.views.programs import (
    fork_program,
    copy_program,
    program_detail,
    program_list,
    program_create,
    add_dailyplan_to_program,
    configure_program
)


from notas.interface.views.profile import profile_detail

from notas.interface.views.authors import (
    author_profile,
    author_programs,
    author_dailyplans,
    author_meals,
)

from notas.interface.views.weight import register_weight
from notas.interface.views.inbox import inbox_list
from notas.interface.views.project import project_view
from notas.interface.views.nutrition import elemental_context, elemental_nutrition, elemental_platform

from notas.interface.views.home import home_view
    
from notas.interface.views.admin_tools import (
    admin_home,
    admin_food_catalog,
    admin_foods_export_csv,
    admin_foods_template,
)



urlpatterns = [
    
    path("", home_view, name="home_view"),

    path("inbox/", inbox_list, name="inbox_list"),
    path("project/", project_view, name="project_view"),

    path("elemental/context/", elemental_context, name="elemental_context"),
    path("elemental/nutrition/", elemental_nutrition, name="elemental_nutrition"),
    path("elemental/platform/", elemental_platform, name="elemental_platform"),


    path("dailyplans/<int:pk>/remove/", dailyplan_remove ,name="dailyplan_remove"),
    path("dailyplans/shared/<int:share_id>/unshare/", dailyplan_unshare ,name="dailyplan_unshare"),
    path("dailyplans/shared/<int:pk>/", dailyplan_shared_detail, name="dailyplan_shared_detail"),
    path("dailyplans/shared/<int:share_id>/dismiss/", dailyplan_share_dismiss, name="dailyplan_share_dismiss"),
    path("dailyplans/shared/", dailyplan_shared_list, name="dailyplan_shared_list"),
    path('dailyplans/<int:dailyplan_id>/save/', dailyplan_save, name='dailyplan_save'),

    path("dailyplans/<int:pk>/share/", dailyplan_share, name="dailyplan_share"),
    path("dailyplans/shared/<uuid:token>/", dailyplan_share_accept, name="dailyplan_share_accept"),


    path("meals/<int:pk>/share/", meal_share, name="meal_share"),
    path("meals/shared/<int:pk>/", meal_share_detail, name="meal_share_detail"),
    path("meals/shared/<uuid:token>/", meal_share_accept, name="meal_share_accept"),
    path("meals/shared/<int:share_id>/dismiss/", meal_share_dismiss, name="meal_share_dismiss"),


    path("meals/draft/<int:pk>/delete/", meal_draft_delete, name="meal_draft_delete"),
    path("meals/draft/", meal_draft_list, name="meal_draft_list"),
    path("meals/shared/", meal_shared_list, name="meal_shared_list"),
    path("meals/<int:pk>/remove/", meal_remove, name="meal_remove"),


    path("meals/shares/<int:share_id>/unshare/", meal_unshare, name="meal_unshare"),




    #FOODS
    path("foods/import/", import_foods, name="import_foods"),
    path("foods/template/", download_food_template, name="download_food_template"),
    path("foods/", food_list, name="food_list"),
    path("foods/<int:pk>/", food_detail, name="food_detail"),
    path("foods/create/", food_create, name="food_create"),
    path("foods/<int:pk>/edit/", food_edit, name="food_edit"),

    #MEALS
    path("meals/", meal_list, name="meal_list"),
    path("meals/explore/", meal_explore_list, name="meal_explore_list"),
    path("meals/<int:pk>/", meal_detail, name="meal_detail"),
    path("meals/explore/<int:pk>/", meal_explore_detail, name="meal_explore_detail"),
    path("meals/create/", meal_create, name="meal_create"),
    path("meals/<int:pk>/rename/", meal_rename, name="meal_rename"),
    path("meals/<int:pk>/configure/", meal_configure, name="meal_configure"),

    path('meals/<int:meal_id>/fork/', meal_fork, name='meal_fork'),
    path("meals/<int:pk>/copy/", meal_copy, name="meal_copy"),
    path("meals/<int:pk>/add-food/", add_food_to_meal, name="add_food_to_meal"),

    #MEAL_FOODS
    path("meal-foods/<int:pk>/remove/", mealfood_remove, name="mealfood_remove"), 
    path("meals/<int:meal_id>/mealfoods/<int:mealfood_id>/update/", mealfood_update, name="mealfood_update"),
    path("meals/<int:meal_id>/add-to-dailyplan/", add_meal_from_list, name="add_meal_from_list"),
    path(
        "meals/<int:meal_id>/foods/reorder/",
        mealfood_reorder,
        name="mealfood_reorder",
    ),




    #DAILY PLANS
    path("dailyplans/", dailyplan_list, name="dailyplan_list"),
    path("dailyplans/<int:pk>/", dailyplan_detail, name="dailyplan_detail"),
    path("dailyplans/explore/", dailyplan_explore_list, name="dailyplan_explore_list"),
    path("dailyplans/explore/<int:pk>/", dailyplan_explore_detail, name="dailyplan_explore_detail"),
    path("dailyplans/draft/", dailyplan_draft_list, name="dailyplan_draft_list"),
    path("dailyplans/draft/<int:pk>/", dailyplan_draft_detail, name="dailyplan_draft_detail"),
    path("dailyplans/create/", dailyplan_create, name="dailyplan_create"),
    path("dailyplans/<int:pk>/rename/", dailyplan_rename, name="dailyplan_rename"),
    path("dailyplans/<int:pk>/configure/", dailyplan_configure, name="dailyplan_configure"),
    path("dailyplans/<int:pk>/add-meal/", dailyplan_add_meal, name="dailyplan_add_meal"),
    path("dailyplans/<int:dailyplan_id>/attach-meal/<int:meal_id>/", attach_meal_to_dailyplan, name="attach_meal_to_dailyplan"),
    path('dailyplans/<int:dailyplan_id>/fork/', dailyplan_fork, name='dailyplan_fork'),
    path("dailyplans/<int:pk>/copy/", dailyplan_copy, name="dailyplan_copy"),
    path("dailyplans/draft/<int:pk>/edit/", dailyplan_draft_edit, name="dailyplan_draft_edit"),

    


    path(
        "dailyplans/<int:dailyplan_id>/meals/create/",
        create_meal_for_dailyplan,
        name="create_meal_for_dailyplan",
    ),



    #DAILYPLAN_MEALS
    path(
        "dailyplans/<int:dailyplan_id>/meals/<int:pk>/",
        dailyplan_meal_detail,
        name="dailyplan_meal_detail"
    ),
    path(
        "dailyplans/<int:dailyplan_id>/meals/<int:dailyplanmeal_id>/update/",
        dailyplanmeal_update,
        name="dailyplanmeal_update"
    ),
    path(
        "dailyplans/<int:dailyplan_id>/meals/<int:dailyplanmeal_id>/edit/",
        dailyplan_meal_edit,
        name="dailyplan_meal_edit"
    ),
    ######
    path(
        "dailyplans/<int:dailyplan_id>/meals/<int:dailyplanmeal_id>/remove/", 
        dailyplanmeal_remove, 
        name="dailyplanmeal_remove"
    ),
    path(
        "dailyplans/<int:dailyplan_id>/meals/<int:dailyplanmeal_id>/replace/",
        replace_dailyplan_meal, 
        name="replace_dailyplan_meal"
    ),
    path(
        "dailyplans/<int:dailyplan_id>/meals/<int:dailyplanmeal_id>/replace/<int:new_meal_id>/", 
        replace_meal, 
        name='replace_meal'
    ),
    path(
        "dailyplans/<int:dailyplan_id>/meals/<int:dailyplanmeal_id>/replace/<int:meal_id>/confirm/",
        confirm_replace_meal,
        name="confirm_replace_meal"
    ),

    path(
        "dailyplans/<int:dailyplan_id>/meals/<int:dailyplanmeal_id>/create/",
        dailyplanmeal_create_meal,
        name="dailyplanmeal_create_meal"
    ),

    path(
        "dailyplans/<int:dailyplan_id>/meals/reorder/",
        dailyplanmeal_reorder,
        name="dailyplanmeal_reorder",
    ),





    #PROGRAMS
    path("programs/", program_list, name="program_list"),
    path("programs/create/", program_create, name="program_create"),
    path("programs/<int:pk>/configure/", configure_program, name="configure_program"),
    path("programs/<int:pk>/add-dailyplan/", add_dailyplan_to_program, name="add_dailyplan_to_program"),
    path("programs/<int:pk>/", program_detail, name="program_detail"),
    path('programs/<int:program_id>/fork/', fork_program, name='fork_program'),
    path("programs/<int:pk>/copy/", copy_program, name="copy_program"),
    

    #PROFILE
    path("profile/", profile_detail, name="profile_detail"),
    path("authors/<str:username>/", author_profile, name="author_profile"),
    path("authors/<str:username>/programs/", author_programs, name="author_programs"),
    path("authors/<str:username>/dailyplans/", author_dailyplans, name="author_dailyplans"),
    path("authors/<str:username>/meals/", author_meals, name="author_meals"),


    #APIS
    path("api/foods/", foods_json, name="foods_json"),


    #WEIGHT
    path("weight/register/", register_weight, name="weight_register"),
    

    #ADMIN
    path("admin-tools/", admin_home, name="admin_home"),
    path("admin-tools/foods/", admin_food_catalog, name="admin_food_catalog"),
    path("admin-tools/foods/export/", admin_foods_export_csv, name="admin_foods_export_csv"),
    path("admin-tools/foods/template/", admin_foods_template, name="admin_foods_template"),


]
