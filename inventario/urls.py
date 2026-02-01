from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.admin_dashboard, name='dashboard'),

    path('entradas/', views.entrada_historial, name='entrada_historial'),
    path('entradas/registrar/', views.entrada_registrar, name='entrada_registrar'),
    path('entradas/<int:pk>/', views.entrada_detalle, name='entrada_detalle'),
    path('api/buscar-producto/', views.buscar_producto, name='buscar_producto'),

    path('inventario-fisico/', views.inventario_sesiones, name='inventario_sesiones'),
    path('inventario-fisico/iniciar/', views.inventario_iniciar, name='inventario_iniciar'),
    path('inventario-fisico/<int:sesion_id>/conteo/', views.inventario_conteo, name='inventario_conteo'),
    path('inventario-fisico/<int:sesion_id>/registrar/', views.inventario_registrar_conteo, name='inventario_registrar_conteo'),
    path('inventario-fisico/<int:sesion_id>/finalizar/', views.inventario_finalizar, name='inventario_finalizar'),
    path('inventario-fisico/<int:sesion_id>/resultados/', views.inventario_resultados, name='inventario_resultados'),
    path('inventario-fisico/<int:sesion_id>/conciliar/', views.inventario_conciliar, name='inventario_conciliar'),
    path('inventario-fisico/<int:sesion_id>/cancelar/', views.inventario_cancelar, name='inventario_cancelar'),
    path('inventario-fisico/<int:sesion_id>/eliminar-conteo/<int:conteo_id>/', views.inventario_eliminar_conteo, name='inventario_eliminar_conteo'),

    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/crear/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_edit, name='categoria_edit'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete, name='categoria_delete'),

    path('proveedores/', views.proveedor_list, name='proveedor_list'),
    path('proveedores/crear/', views.proveedor_create, name='proveedor_create'),
    path('proveedores/<int:pk>/editar/', views.proveedor_edit, name='proveedor_edit'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_delete, name='proveedor_delete'),

    path('productos/', views.producto_list, name='producto_list'),
    path('productos/crear/', views.producto_create, name='producto_create'),
    path('productos/<int:pk>/editar/', views.producto_edit, name='producto_edit'),
    path('productos/<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),

    path('usuarios/', views.usuario_list, name='usuario_list'),
    path('usuarios/crear/', views.usuario_create, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_edit, name='usuario_edit'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_delete, name='usuario_delete'),

    path('perfil/', views.perfil_edit, name='perfil_edit'),
]
