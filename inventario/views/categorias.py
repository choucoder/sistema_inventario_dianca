from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Category, Product


@login_required
def categoria_list(request):
    categorias = Category.objects.all().order_by('name')
    return render(request, 'categorias/list.html', {'categorias': categorias})


@login_required
def categoria_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'El nombre de la categoria es requerido.')
            return render(request, 'categorias/form.html', {
                'name': name,
                'description': description,
            })

        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, 'Ya existe una categoria con ese nombre.')
            return render(request, 'categorias/form.html', {
                'name': name,
                'description': description,
            })

        Category.objects.create(
            name=name,
            description=description,
            status='active'
        )
        messages.success(request, f'Categoria "{name}" creada exitosamente.')
        return redirect('categoria_list')

    return render(request, 'categorias/form.html', {'name': '', 'description': ''})


@login_required
def categoria_edit(request, pk):
    categoria = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', 'active')

        if not name:
            messages.error(request, 'El nombre de la categoria es requerido.')
            return render(request, 'categorias/form.html', {
                'categoria': categoria,
                'name': name,
                'description': description,
            })

        if Category.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, 'Ya existe otra categoria con ese nombre.')
            return render(request, 'categorias/form.html', {
                'categoria': categoria,
                'name': name,
                'description': description,
            })

        categoria.name = name
        categoria.description = description
        categoria.status = status
        categoria.save()

        messages.success(request, f'Categoria "{name}" actualizada exitosamente.')
        return redirect('categoria_list')

    return render(request, 'categorias/form.html', {'categoria': categoria})


@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Category, pk=pk)

    productos_count = Product.objects.filter(category=categoria).count()
    if productos_count > 0:
        messages.error(
            request,
            f'No se puede eliminar la categoria "{categoria.name}" porque tiene {productos_count} producto(s) asociado(s).'
        )
        return redirect('categoria_list')

    if request.method == 'POST':
        name = categoria.name
        categoria.delete()
        messages.success(request, f'Categoria "{name}" eliminada exitosamente.')
        return redirect('categoria_list')

    return render(request, 'categorias/delete.html', {'categoria': categoria})
