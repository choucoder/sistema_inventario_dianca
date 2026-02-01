from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def perfil_edit(request):
    usuario = request.user

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        errors = False

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
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
                errors = True
            if password != password_confirm:
                messages.error(request, 'Las contraseñas no coinciden.')
                errors = True

        if errors:
            return render(request, 'perfil/edit.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
            })

        usuario.first_name = first_name
        usuario.last_name = last_name
        usuario.email = email

        if password:
            usuario.set_password(password)

        usuario.save()

        if password:
            messages.success(request, 'Perfil actualizado. Por favor inicie sesion nuevamente.')
            return redirect('login')

        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('perfil_edit')

    return render(request, 'perfil/edit.html')
