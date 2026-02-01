from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps

from ..models import User


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'admin':
            messages.error(request, 'No tiene permisos para acceder a esta seccion.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def usuario_list(request):
    usuarios = User.objects.all().order_by('username')
    return render(request, 'usuarios/list.html', {'usuarios': usuarios})


@login_required
@admin_required
def usuario_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        role = request.POST.get('role', 'almacen')

        errors = False

        if not username:
            messages.error(request, 'El nombre de usuario es requerido.')
            errors = True
        elif len(username) > 150:
            messages.error(request, 'El nombre de usuario no puede exceder 150 caracteres.')
            errors = True

        if username and User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Ya existe un usuario con ese nombre de usuario.')
            errors = True

        if not first_name:
            messages.error(request, 'El nombre es requerido.')
            errors = True
        elif len(first_name) > 150:
            messages.error(request, 'El nombre no puede exceder 150 caracteres.')
            errors = True

        if len(last_name) > 150:
            messages.error(request, 'El apellido no puede exceder 150 caracteres.')
            errors = True

        if not password:
            messages.error(request, 'La Contraseña es requerida.')
            errors = True
        elif len(password) < 8:
            messages.error(request, 'La Contraseña debe tener al menos 8 caracteres.')
            errors = True

        if password != password_confirm:
            messages.error(request, 'Las Contraseñas no coinciden.')
            errors = True

        if role not in dict(User.ROLES):
            messages.error(request, 'El rol seleccionado no es valido.')
            errors = True

        if errors:
            return render(request, 'usuarios/form.html', {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'roles': User.ROLES,
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            status='active'
        )

        messages.success(request, f'Usuario "{username}" creado exitosamente.')
        return redirect('usuario_list')

    return render(request, 'usuarios/form.html', {
        'username': '',
        'first_name': '',
        'last_name': '',
        'role': 'almacen',
        'roles': User.ROLES,
    })


@login_required
@admin_required
def usuario_edit(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        role = request.POST.get('role', usuario.role)
        status = request.POST.get('status', 'active')

        errors = False

        if not username:
            messages.error(request, 'El nombre de usuario es requerido.')
            errors = True
        elif len(username) > 150:
            messages.error(request, 'El nombre de usuario no puede exceder 150 caracteres.')
            errors = True

        if username and User.objects.filter(username__iexact=username).exclude(pk=pk).exists():
            messages.error(request, 'Ya existe otro usuario con ese nombre de usuario.')
            errors = True

        if not first_name:
            messages.error(request, 'El nombre es requerido.')
            errors = True
        elif len(first_name) > 150:
            messages.error(request, 'El nombre no puede exceder 150 caracteres.')
            errors = True

        if len(last_name) > 150:
            messages.error(request, 'El apellido no puede exceder 150 caracteres.')
            errors = True

        if password:
            if len(password) < 8:
                messages.error(request, 'La Contraseña debe tener al menos 8 caracteres.')
                errors = True
            if password != password_confirm:
                messages.error(request, 'Las Contraseñas no coinciden.')
                errors = True

        if role not in dict(User.ROLES):
            messages.error(request, 'El rol seleccionado no es valido.')
            errors = True

        if usuario.role == 'admin' and usuario.pk == 1 and role != 'admin':
            messages.error(request, 'No se puede cambiar el rol del administrador principal.')
            errors = True

        if errors:
            return render(request, 'usuarios/form.html', {
                'usuario': usuario,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'roles': User.ROLES,
            })

        usuario.username = username
        usuario.first_name = first_name
        usuario.last_name = last_name
        usuario.role = role
        usuario.status = status

        if password:
            usuario.set_password(password)

        usuario.save()

        messages.success(request, f'Usuario "{username}" actualizado exitosamente.')
        return redirect('usuario_list')

    return render(request, 'usuarios/form.html', {
        'usuario': usuario,
        'roles': User.ROLES,
    })


@login_required
@admin_required
def usuario_delete(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if usuario.role == 'admin':
        admin_count = User.objects.filter(role='admin').count()
        if admin_count <= 1:
            messages.error(request, 'No se puede eliminar al unico administrador del sistema.')
            return redirect('usuario_list')

    if usuario.pk == request.user.pk:
        messages.error(request, 'No puede eliminarse a si mismo.')
        return redirect('usuario_list')

    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{username}" eliminado exitosamente.')
        return redirect('usuario_list')

    return render(request, 'usuarios/delete.html', {'usuario': usuario})
