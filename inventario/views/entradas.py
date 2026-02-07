from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal, InvalidOperation

from ..models import Entrada, Product, Provider


@login_required
def entrada_registrar(request):
    proveedores = Provider.objects.filter(status='active').order_by('name')

    if request.method == 'POST':
        product_code = request.POST.get('product_code', '').strip()
        provider_id = request.POST.get('provider', '')
        quantity = request.POST.get('quantity', '').strip()
        total_cost = request.POST.get('total_cost', '').strip()

        errors = False

        if not product_code:
            messages.error(request, 'El codigo del producto es requerido.')
            errors = True
            product = None
        else:
            try:
                product = Product.objects.get(code__iexact=product_code)
                if product.status != 'active':
                    messages.error(request, 'El producto no esta activo.')
                    errors = True
            except Product.DoesNotExist:
                messages.error(request, f'No existe un producto con el codigo "{product_code}".')
                errors = True
                product = None

        if not provider_id:
            messages.error(request, 'El proveedor es requerido.')
            errors = True
            provider = None
        else:
            try:
                provider = Provider.objects.get(pk=provider_id, status='active')
            except Provider.DoesNotExist:
                messages.error(request, 'El proveedor seleccionado no es valido.')
                errors = True
                provider = None

        try:
            quantity_int = int(quantity) if quantity else 0
            if quantity_int <= 0:
                messages.error(request, 'La cantidad debe ser mayor a cero.')
                errors = True
        except ValueError:
            messages.error(request, 'La cantidad debe ser un numero entero.')
            errors = True
            quantity_int = 0

        try:
            total_cost_decimal = Decimal(total_cost) if total_cost else Decimal('0')
            if total_cost_decimal < 0:
                messages.error(request, 'El costo total no puede ser negativo.')
                errors = True
        except InvalidOperation:
            messages.error(request, 'El costo total debe ser un numero valido.')
            errors = True
            total_cost_decimal = Decimal('0')

        if errors:
            return render(request, 'entradas/registrar.html', {
                'proveedores': proveedores,
                'product_code': product_code,
                'provider_id': provider_id,
                'quantity': quantity,
                'total_cost': total_cost,
                'product': product if 'product' in dir() and product else None,
            })

        entrada = Entrada.objects.create(
            product=product,
            provider=provider,
            user=request.user,
            quantity=quantity_int,
            total_cost=total_cost_decimal
        )

        stock_msg = ''
        if product.stock_actual > product.min_stock:
            stock_msg = f' El producto ya no esta en alerta de stock bajo.'
        elif product.stock_actual <= product.min_stock:
            stock_msg = f' Atencion: El producto aun esta en alerta de stock bajo ({product.stock_actual}/{product.min_stock}).'

        messages.success(
            request,
            f'Entrada registrada exitosamente. Se agregaron {quantity_int} {product.unit} de "{product.name}".{stock_msg}'
        )
        return redirect('entrada_historial')

    return render(request, 'entradas/registrar.html', {
        'proveedores': proveedores,
        'product_code': '',
        'provider_id': '',
        'quantity': '',
        'total_cost': '',
    })


@login_required
def entrada_historial(request):
    entradas = Entrada.objects.select_related(
        'product', 'provider', 'user'
    ).order_by('-created_at')

    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    producto = request.GET.get('producto', '')
    proveedor = request.GET.get('proveedor', '')

    if fecha_desde:
        entradas = entradas.filter(created_at__date__gte=fecha_desde)

    if fecha_hasta:
        entradas = entradas.filter(created_at__date__lte=fecha_hasta)

    if producto:
        entradas = entradas.filter(
            Q(product__code__icontains=producto) |
            Q(product__name__icontains=producto)
        )

    if proveedor:
        entradas = entradas.filter(provider_id=proveedor)

    proveedores = Provider.objects.all().order_by('name')

    return render(request, 'entradas/historial.html', {
        'entradas': entradas,
        'proveedores': proveedores,
        'filtros': {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'producto': producto,
            'proveedor': proveedor,
        }
    })


@login_required
def buscar_producto(request):
    code = request.GET.get('code', '').strip()

    if not code:
        return JsonResponse({'found': False, 'error': 'Codigo no proporcionado'})

    try:
        product = Product.objects.select_related('category').get(code__iexact=code)

        if product.stock_actual <= product.min_stock:
            stock_status = 'danger'
            stock_message = f'ALERTA: Stock bajo el minimo ({product.min_stock})'
        else:
            stock_status = 'success'
            stock_message = 'Stock normal'

        return JsonResponse({
            'found': True,
            'product': {
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'unit': product.unit,
                'category': product.category.name,
                'stock_actual': product.stock_actual,
                'min_stock': product.min_stock,
                'location': product.location or 'No especificada',
                'status': product.status,
                'stock_status': stock_status,
                'stock_message': stock_message,
            }
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'found': False,
            'error': f'No existe producto con codigo "{code}"'
        })


@login_required
def buscar_productos_autocomplete(request):
    """
    Endpoint para busqueda asincrona de productos por nombre o codigo.
    Retorna una lista de productos que coinciden con el termino de busqueda.
    """
    term = request.GET.get('term', '').strip()

    if not term or len(term) < 2:
        return JsonResponse([], safe=False)

    # Buscar productos activos por codigo o nombre
    productos = Product.objects.filter(
        Q(code__icontains=term) | Q(name__icontains=term),
        status='active'
    ).select_related('category').order_by('name')[:15]

    resultados = []
    for producto in productos:
        resultados.append({
            'id': producto.id,
            'code': producto.code,
            'name': producto.name,
            'label': f"{producto.code} - {producto.name}",
            'value': producto.code,
            'category': producto.category.name,
            'unit': producto.unit,
            'stock_actual': producto.stock_actual,
            'min_stock': producto.min_stock,
            'location': producto.location or 'No especificada',
        })

    return JsonResponse(resultados, safe=False)


@login_required
def entrada_detalle(request, pk):
    entrada = get_object_or_404(
        Entrada.objects.select_related('product', 'provider', 'user'),
        pk=pk
    )
    return render(request, 'entradas/detalle.html', {'entrada': entrada})
