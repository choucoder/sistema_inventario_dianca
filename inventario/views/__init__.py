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
)
from .entradas import (
    entrada_registrar,
    entrada_historial,
    entrada_detalle,
    buscar_producto,
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
)
from .perfil import perfil_edit
