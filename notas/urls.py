from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    lista_notas, crear_nota, editar_nota, borrar_nota,
    signup_view, lista_productos, crear_producto
)

urlpatterns = [
    path('notas/', views.lista_notas, name='lista_notas'),
    path('crear/', views.crear_nota, name='crear_nota'),
    path('editar/<int:id>/', views.editar_nota, name='editar_nota'),
    path('borrar/<int:id>/', views.borrar_nota, name='borrar_nota'),
    
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', signup_view, name='signup'),   # <<--- NUEVO

    path('productos/', lista_productos, name='lista_productos'),
    path('productos/crear/', crear_producto, name='crear_producto'),

    path('productos/<int:id>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),

    path('htmx/agregar-producto/', views.htmx_agregar_producto, name='htmx_agregar_producto'),
    path('htmx/eliminar/', views.htmx_eliminar_producto, name='htmx_eliminar_producto'),




]