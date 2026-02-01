from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Product, Category, Entrada, InventoryAdjustment


@login_required
def producto_list(request):
    productos = Product.objects.select_related('category').all().order_by('name')
    return render(request, 'productos/list.html', {'productos': productos})


@login_required
def producto_create(request):
    categorias = Category.objects.filter(status='active').order_by('name')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        unit = request.POST.get('unit', '').strip()
        min_stock = request.POST.get('min_stock', '0').strip()
        category_id = request.POST.get('category', '')
        location = request.POST.get('location', '').strip()

        errors = False

        if not code:
            messages.error(request, 'El codigo del producto es requerido.')
            errors = True
        elif len(code) > 50:
            messages.error(request, 'El codigo no puede exceder 50 caracteres.')
            errors = True

        if code and Product.objects.filter(code__iexact=code).exists():
            messages.error(request, 'Ya existe un producto con ese codigo.')
            errors = True

        if not name:
            messages.error(request, 'El nombre del producto es requerido.')
            errors = True
        elif len(name) > 200:
            messages.error(request, 'El nombre no puede exceder 200 caracteres.')
            errors = True

        if not unit:
            messages.error(request, 'La unidad de medida es requerida.')
            errors = True
        elif len(unit) > 20:
            messages.error(request, 'La unidad no puede exceder 20 caracteres.')
            errors = True

        if not category_id:
            messages.error(request, 'La categoria es requerida.')
            errors = True

        if len(location) > 100:
            messages.error(request, 'La ubicacion no puede exceder 100 caracteres.')
            errors = True

        try:
            min_stock_int = int(min_stock) if min_stock else 0
            if min_stock_int < 0:
                messages.error(request, 'El stock minimo no puede ser negativo.')
                errors = True
        except ValueError:
            messages.error(request, 'El stock minimo debe ser un numero entero.')
            errors = True
            min_stock_int = 0

        if errors:
            return render(request, 'productos/form.html', {
                'categorias': categorias,
                'code': code,
                'name': name,
                'description': description,
                'unit': unit,
                'min_stock': min_stock,
                'category_id': category_id,
                'location': location,
            })

        category = get_object_or_404(Category, pk=category_id)

        Product.objects.create(
            code=code,
            name=name,
            description=description or None,
            unit=unit,
            min_stock=min_stock_int,
            stock_actual=0,
            category=category,
            location=location,
            status='active'
        )
        messages.success(request, f'Producto "{name}" creado exitosamente.')
        return redirect('producto_list')

    return render(request, 'productos/form.html', {
        'categorias': categorias,
        'code': '',
        'name': '',
        'description': '',
        'unit': '',
        'min_stock': '0',
        'category_id': '',
        'location': '',
    })


@login_required
def producto_edit(request, pk):
    producto = get_object_or_404(Product, pk=pk)
    categorias = Category.objects.filter(status='active').order_by('name')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        unit = request.POST.get('unit', '').strip()
        min_stock = request.POST.get('min_stock', '0').strip()
        category_id = request.POST.get('category', '')
        location = request.POST.get('location', '').strip()
        status = request.POST.get('status', 'active')

        errors = False

        if not code:
            messages.error(request, 'El codigo del producto es requerido.')
            errors = True
        elif len(code) > 50:
            messages.error(request, 'El codigo no puede exceder 50 caracteres.')
            errors = True

        if code and Product.objects.filter(code__iexact=code).exclude(pk=pk).exists():
            messages.error(request, 'Ya existe otro producto con ese codigo.')
            errors = True

        if not name:
            messages.error(request, 'El nombre del producto es requerido.')
            errors = True
        elif len(name) > 200:
            messages.error(request, 'El nombre no puede exceder 200 caracteres.')
            errors = True

        if not unit:
            messages.error(request, 'La unidad de medida es requerida.')
            errors = True
        elif len(unit) > 20:
            messages.error(request, 'La unidad no puede exceder 20 caracteres.')
            errors = True

        if not category_id:
            messages.error(request, 'La categoria es requerida.')
            errors = True

        if len(location) > 100:
            messages.error(request, 'La ubicacion no puede exceder 100 caracteres.')
            errors = True

        try:
            min_stock_int = int(min_stock) if min_stock else 0
            if min_stock_int < 0:
                messages.error(request, 'El stock minimo no puede ser negativo.')
                errors = True
        except ValueError:
            messages.error(request, 'El stock minimo debe ser un numero entero.')
            errors = True
            min_stock_int = 0

        if errors:
            return render(request, 'productos/form.html', {
                'producto': producto,
                'categorias': categorias,
                'code': code,
                'name': name,
                'description': description,
                'unit': unit,
                'min_stock': min_stock,
                'category_id': category_id,
                'location': location,
            })

        category = get_object_or_404(Category, pk=category_id)

        producto.code = code
        producto.name = name
        producto.description = description or None
        producto.unit = unit
        producto.min_stock = min_stock_int
        producto.category = category
        producto.location = location
        producto.status = status
        producto.save()

        messages.success(request, f'Producto "{name}" actualizado exitosamente.')
        return redirect('producto_list')

    return render(request, 'productos/form.html', {
        'producto': producto,
        'categorias': categorias,
    })


@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Product, pk=pk)

    entradas_count = Entrada.objects.filter(product=producto).count()
    if entradas_count > 0:
        messages.error(
            request,
            f'No se puede eliminar el producto "{producto.name}" porque tiene {entradas_count} entrada(s) asociada(s).'
        )
        return redirect('producto_list')

    ajustes_count = InventoryAdjustment.objects.filter(product=producto).count()
    if ajustes_count > 0:
        messages.error(
            request,
            f'No se puede eliminar el producto "{producto.name}" porque tiene {ajustes_count} ajuste(s) de inventario asociado(s).'
        )
        return redirect('producto_list')

    if request.method == 'POST':
        name = producto.name
        producto.delete()
        messages.success(request, f'Producto "{name}" eliminado exitosamente.')
        return redirect('producto_list')

    return render(request, 'productos/delete.html', {'producto': producto})
