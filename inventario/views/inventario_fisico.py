from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction

from ..models import Product, InventarioSesion, DetalleConteo, InventoryAdjustment


@login_required
def inventario_sesiones(request):
    sesiones = InventarioSesion.objects.select_related('user').order_by('-created_at')
    return render(request, 'inventario_fisico/sesiones.html', {'sesiones': sesiones})


@login_required
def inventario_iniciar(request):
    sesion_activa = InventarioSesion.objects.filter(
        user=request.user,
        status='en_proceso'
    ).first()

    if sesion_activa:
        messages.warning(request, 'Ya tiene una sesion de inventario en proceso.')
        return redirect('inventario_conteo', sesion_id=sesion_activa.pk)

    if request.method == 'POST':
        notas = request.POST.get('notas', '').strip()

        sesion = InventarioSesion.objects.create(
            user=request.user,
            notas=notas,
            status='en_proceso'
        )

        messages.success(request, f'Sesion de inventario #{sesion.pk} iniciada. Puede comenzar a escanear productos.')
        return redirect('inventario_conteo', sesion_id=sesion.pk)

    return render(request, 'inventario_fisico/iniciar.html')


@login_required
def inventario_conteo(request, sesion_id):
    sesion = get_object_or_404(InventarioSesion, pk=sesion_id)

    if sesion.user != request.user and request.user.role != 'admin':
        messages.error(request, 'No tiene permiso para acceder a esta sesion.')
        return redirect('inventario_sesiones')

    if sesion.status in ['finalizado', 'conciliado']:
        return redirect('inventario_resultados', sesion_id=sesion.pk)

    conteos = sesion.detalles.select_related('product').order_by('-created_at')

    return render(request, 'inventario_fisico/conteo.html', {
        'sesion': sesion,
        'conteos': conteos,
    })


@login_required
def inventario_registrar_conteo(request, sesion_id):
    sesion = get_object_or_404(InventarioSesion, pk=sesion_id)

    if sesion.status != 'en_proceso':
        return JsonResponse({
            'success': False,
            'error': 'La sesion no esta en proceso.'
        })

    if request.method == 'POST':
        product_code = request.POST.get('product_code', '').strip()
        cantidad = request.POST.get('cantidad', '').strip()

        try:
            product = Product.objects.get(code__iexact=product_code)
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'No existe producto con codigo "{product_code}"'
            })

        try:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                return JsonResponse({
                    'success': False,
                    'error': 'La cantidad no puede ser negativa.'
                })
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'La cantidad debe ser un numero entero.'
            })

        conteo_existente = DetalleConteo.objects.filter(
            sesion=sesion,
            product=product
        ).first()

        stock_sistema = product.stock_actual
        diferencia = cantidad_int - stock_sistema

        if conteo_existente:
            conteo_existente.cantidad_contada = cantidad_int
            conteo_existente.diferencia = diferencia
            conteo_existente.updated_at = timezone.now()
            conteo_existente.save()
            mensaje = f'Conteo actualizado para "{product.name}"'
        else:
            DetalleConteo.objects.create(
                sesion=sesion,
                product=product,
                stock_sistema=stock_sistema,
                cantidad_contada=cantidad_int,
                diferencia=diferencia
            )
            mensaje = f'Conteo registrado para "{product.name}"'

        sesion.total_productos = sesion.detalles.count()
        sesion.save()

        return JsonResponse({
            'success': True,
            'message': mensaje,
            'data': {
                'product_name': product.name,
                'product_code': product.code,
                'stock_sistema': stock_sistema,
                'cantidad_contada': cantidad_int,
                'diferencia': diferencia,
                'unit': product.unit,
            }
        })

    return JsonResponse({'success': False, 'error': 'Metodo no permitido'})


@login_required
def inventario_finalizar(request, sesion_id):
    sesion = get_object_or_404(InventarioSesion, pk=sesion_id)

    if sesion.status != 'en_proceso':
        messages.error(request, 'Esta sesion ya fue finalizada.')
        return redirect('inventario_resultados', sesion_id=sesion.pk)

    if sesion.detalles.count() == 0:
        messages.error(request, 'No puede finalizar una sesion sin conteos.')
        return redirect('inventario_conteo', sesion_id=sesion.pk)

    if request.method == 'POST':
        conteos_con_diferencia = sesion.detalles.exclude(diferencia=0).count()

        sesion.status = 'finalizado'
        sesion.finished_at = timezone.now()
        sesion.productos_con_diferencia = conteos_con_diferencia
        sesion.save()

        if conteos_con_diferencia > 0:
            messages.warning(
                request,
                f'Sesion finalizada. Se encontraron {conteos_con_diferencia} producto(s) con diferencias.'
            )
        else:
            messages.success(
                request,
                'Sesion finalizada. El inventario fisico coincide con el sistema.'
            )

        return redirect('inventario_resultados', sesion_id=sesion.pk)

    return redirect('inventario_conteo', sesion_id=sesion.pk)


@login_required
def inventario_resultados(request, sesion_id):
    sesion = get_object_or_404(InventarioSesion, pk=sesion_id)

    if sesion.status == 'en_proceso':
        return redirect('inventario_conteo', sesion_id=sesion.pk)

    conteos = sesion.detalles.select_related('product').order_by('product__name')
    conteos_con_diferencia = conteos.exclude(diferencia=0)
    conteos_correctos = conteos.filter(diferencia=0)

    return render(request, 'inventario_fisico/resultados.html', {
        'sesion': sesion,
        'conteos': conteos,
        'conteos_con_diferencia': conteos_con_diferencia,
        'conteos_correctos': conteos_correctos,
    })


@login_required
@transaction.atomic
def inventario_conciliar(request, sesion_id):
    sesion = get_object_or_404(InventarioSesion, pk=sesion_id)

    if sesion.status != 'finalizado':
        messages.error(request, 'Solo se pueden conciliar sesiones finalizadas.')
        return redirect('inventario_resultados', sesion_id=sesion.pk)

    if request.method == 'POST':
        conteos_con_diferencia = sesion.detalles.exclude(diferencia=0)

        ajustes_realizados = 0

        for conteo in conteos_con_diferencia:
            InventoryAdjustment.objects.create(
                product=conteo.product,
                user=request.user,
                system_qty=conteo.stock_sistema,
                physical_qty=conteo.cantidad_contada,
                difference=conteo.diferencia
            )

            conteo.product.stock_actual = conteo.cantidad_contada
            conteo.product.save()

            ajustes_realizados += 1

        sesion.status = 'conciliado'
        sesion.conciliated_at = timezone.now()
        sesion.save()

        messages.success(
            request,
            f'Inventario conciliado exitosamente. Se ajustaron {ajustes_realizados} producto(s).'
        )

        return redirect('inventario_resultados', sesion_id=sesion.pk)

    return redirect('inventario_resultados', sesion_id=sesion.pk)


@login_required
def inventario_cancelar(request, sesion_id):
    sesion = get_object_or_404(InventarioSesion, pk=sesion_id)

    if sesion.status not in ['en_proceso', 'finalizado']:
        messages.error(request, 'No se puede cancelar esta sesion.')
        return redirect('inventario_sesiones')

    if request.method == 'POST':
        sesion.status = 'cancelado'
        sesion.save()
        messages.info(request, f'Sesion #{sesion.pk} cancelada.')
        return redirect('inventario_sesiones')

    return render(request, 'inventario_fisico/cancelar.html', {'sesion': sesion})


@login_required
def inventario_eliminar_conteo(request, sesion_id, conteo_id):
    sesion = get_object_or_404(InventarioSesion, pk=sesion_id)

    if sesion.status != 'en_proceso':
        return JsonResponse({
            'success': False,
            'error': 'No se pueden eliminar conteos de sesiones finalizadas.'
        })

    conteo = get_object_or_404(DetalleConteo, pk=conteo_id, sesion=sesion)

    product_name = conteo.product.name
    conteo.delete()

    sesion.total_productos = sesion.detalles.count()
    sesion.save()

    return JsonResponse({
        'success': True,
        'message': f'Conteo de "{product_name}" eliminado.'
    })
