from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.utils import timezone

from ..models import Product, Entrada, Provider


@login_required
def admin_dashboard(request):
    alertas = Product.objects.filter(stock_actual__lt=F('min_stock'))
    total_productos = Product.objects.filter(status='active').count()
    total_proveedores = Provider.objects.filter(status='active').count()
    ultimas_entradas = Entrada.objects.select_related('product', 'provider').order_by('-created_at')[:5]

    hoy = timezone.now().date()
    entradas_hoy = Entrada.objects.filter(created_at__date=hoy).count()

    return render(request, 'dashboard.html', {
        'alertas': alertas,
        'total_productos': total_productos,
        'total_proveedores': total_proveedores,
        'ultimas_entradas': ultimas_entradas,
        'entradas_hoy': entradas_hoy,
    })
