from .auth import login_view, logout_view
from .dashboard import admin_dashboard
from .categorias import (
    categoria_list,
    categoria_create,
    categoria_edit,
    categoria_delete,
)
from .proveedores import (
    proveedor_list,
    proveedor_create,
    proveedor_edit,
    proveedor_delete,
)
from .productos import (
    producto_list,
    producto_create,
    producto_edit,
    producto_delete,
    exportar_inventario_actual,
)
from .entradas import (
    entrada_registrar,
    entrada_historial,
    entrada_detalle,
    buscar_producto,
    buscar_productos_autocomplete,
)
from .usuarios import (
    usuario_list,
    usuario_create,
    usuario_edit,
    usuario_delete,
)
from .inventario_fisico import (
    inventario_sesiones,
    inventario_iniciar,
    inventario_conteo,
    inventario_registrar_conteo,
    inventario_finalizar,
    inventario_resultados,
    inventario_conciliar,
    inventario_cancelar,
    inventario_eliminar_conteo,
    exportar_reporte_auditoria,
)
from .salidas import (
    salida_registrar,
    salida_historial,
    salida_detalle,
    exportar_reporte_salidas,
)
from .perfil import perfil_edit
