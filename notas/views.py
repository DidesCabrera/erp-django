from django.shortcuts import render, redirect, get_object_or_404
from .models import Nota, Producto, NotaProducto
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('lista_notas')
        
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()          # crea el usuario
            login(request, usuario)        # inicia sesión automáticamente
            return redirect('lista_notas') # redirige al home
    else:
        form = UserCreationForm()

    return render(request, "signup.html", {"form": form})


@login_required
def lista_notas(request):
    notas = Nota.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'notas/lista_notas.html', {'notas': notas})


@login_required
def crear_nota(request):
    productos = Producto.objects.all()

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        contenido = request.POST.get("contenido")

        nota = Nota.objects.create(
            titulo=titulo,
            contenido=contenido,
            usuario=request.user
        )

        # agregar productos enviados por HTMX
        productos_ids = request.POST.getlist("productos[]")
        for pid in productos_ids:
            NotaProducto.objects.create(nota=nota, producto_id=pid)

        return redirect('lista_notas')

    return render(request, "notas/crear_nota.html", {"productos": productos})


def htmx_agregar_producto(request):
    producto_id = request.POST.get("producto_id")

    if not producto_id:
        return render(request, "notas/partials/error.html", {"msg": "No llegó producto_id"})

    producto = get_object_or_404(Producto, id=producto_id)

    return render(request, "notas/partials/item_producto.html", {
        "producto": producto
    })





# Vista HTMX para eliminar item temporal
@login_required
def htmx_eliminar_producto(request):
    item_id = request.POST.get("id")
    return render(request, "notas/partials/item_removed.html")














@login_required
def editar_nota(request, id):
    nota = Nota.objects.get(id=id)

    if nota.usuario != request.user:
        return redirect('lista_notas')

    if request.method == 'POST':
        nota.titulo = request.POST['titulo']
        nota.contenido = request.POST['contenido']
        nota.save()
        return redirect('lista_notas')

    return render(request, 'notas/editar_nota.html', {'nota': nota})

@login_required
def borrar_nota(request, id):
    nota = Nota.objects.get(id=id)
    if nota.usuario != request.user:
        return redirect('lista_notas')
    nota.delete()
    return redirect('lista_notas')


@login_required
def lista_productos(request):
    productos = Producto.objects.filter(usuario=request.user)
    return render(request, 'notas/lista_productos.html', {'productos': productos})


@login_required
def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')

        Producto.objects.create(
            nombre=nombre,
            precio=precio,
            usuario=request.user
        )

        return redirect('lista_productos')

    return render(request, 'notas/crear_producto.html')



@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')

        producto.nombre = nombre
        producto.precio = precio
        producto.save()

        return redirect('lista_productos')

    return render(request, 'notas/editar_producto.html', {'producto': producto})


@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')

    return render(request, 'notas/eliminar_producto.html', {'producto': producto})
