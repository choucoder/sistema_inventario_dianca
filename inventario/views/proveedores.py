from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Provider, Entrada, PurchaseOrder


@login_required
def proveedor_list(request):
    proveedores = Provider.objects.all().order_by('name')
    return render(request, 'proveedores/list.html', {'proveedores': proveedores})


@login_required
def proveedor_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        rif = request.POST.get('rif', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        contact_name = request.POST.get('contact_name', '').strip()

        errors = False

        if not name:
            messages.error(request, 'El nombre del proveedor es requerido.')
            errors = True
        elif len(name) > 50:
            messages.error(request, 'El nombre no puede exceder 50 caracteres.')
            errors = True

        if not rif:
            messages.error(request, 'El RIF del proveedor es requerido.')
            errors = True
        elif len(rif) > 12:
            messages.error(request, 'El RIF no puede exceder 12 caracteres.')
            errors = True

        if rif and Provider.objects.filter(rif__iexact=rif).exists():
            messages.error(request, 'Ya existe un proveedor con ese RIF.')
            errors = True

        if len(phone) > 12:
            messages.error(request, 'El telefono no puede exceder 12 caracteres.')
            errors = True

        if len(contact_name) > 50:
            messages.error(request, 'El nombre de contacto no puede exceder 50 caracteres.')
            errors = True

        if errors:
            return render(request, 'proveedores/form.html', {
                'name': name,
                'rif': rif,
                'phone': phone,
                'email': email,
                'contact_name': contact_name,
            })

        Provider.objects.create(
            name=name,
            rif=rif,
            phone=phone,
            email=email,
            contact_name=contact_name,
            status='active'
        )
        messages.success(request, f'Proveedor "{name}" creado exitosamente.')
        return redirect('proveedor_list')

    return render(request, 'proveedores/form.html', {
        'name': '',
        'rif': '',
        'phone': '',
        'email': '',
        'contact_name': '',
    })


@login_required
def proveedor_edit(request, pk):
    proveedor = get_object_or_404(Provider, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        rif = request.POST.get('rif', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        contact_name = request.POST.get('contact_name', '').strip()
        status = request.POST.get('status', 'active')

        errors = False

        if not name:
            messages.error(request, 'El nombre del proveedor es requerido.')
            errors = True
        elif len(name) > 50:
            messages.error(request, 'El nombre no puede exceder 50 caracteres.')
            errors = True

        if not rif:
            messages.error(request, 'El RIF del proveedor es requerido.')
            errors = True
        elif len(rif) > 12:
            messages.error(request, 'El RIF no puede exceder 12 caracteres.')
            errors = True

        if rif and Provider.objects.filter(rif__iexact=rif).exclude(pk=pk).exists():
            messages.error(request, 'Ya existe otro proveedor con ese RIF.')
            errors = True

        if len(phone) > 12:
            messages.error(request, 'El telefono no puede exceder 12 caracteres.')
            errors = True

        if len(contact_name) > 50:
            messages.error(request, 'El nombre de contacto no puede exceder 50 caracteres.')
            errors = True

        if errors:
            return render(request, 'proveedores/form.html', {
                'proveedor': proveedor,
                'name': name,
                'rif': rif,
                'phone': phone,
                'email': email,
                'contact_name': contact_name,
            })

        proveedor.name = name
        proveedor.rif = rif
        proveedor.phone = phone
        proveedor.email = email
        proveedor.contact_name = contact_name
        proveedor.status = status
        proveedor.save()

        messages.success(request, f'Proveedor "{name}" actualizado exitosamente.')
        return redirect('proveedor_list')

    return render(request, 'proveedores/form.html', {'proveedor': proveedor})


@login_required
def proveedor_delete(request, pk):
    proveedor = get_object_or_404(Provider, pk=pk)

    entradas_count = Entrada.objects.filter(provider=proveedor).count()
    if entradas_count > 0:
        messages.error(
            request,
            f'No se puede eliminar el proveedor "{proveedor.name}" porque tiene {entradas_count} entrada(s) asociada(s).'
        )
        return redirect('proveedor_list')

    ordenes_count = PurchaseOrder.objects.filter(provider=proveedor).count()
    if ordenes_count > 0:
        messages.error(
            request,
            f'No se puede eliminar el proveedor "{proveedor.name}" porque tiene {ordenes_count} orden(es) de compra asociada(s).'
        )
        return redirect('proveedor_list')

    if request.method == 'POST':
        name = proveedor.name
        proveedor.delete()
        messages.success(request, f'Proveedor "{name}" eliminado exitosamente.')
        return redirect('proveedor_list')

    return render(request, 'proveedores/delete.html', {'proveedor': proveedor})
