from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('status', 'active')
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('almacen', 'Empleado de Almacén'),
        ('ventas', 'Ventas'),
        ('compras', 'Compras'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='almacen')
    status = models.CharField(max_length=20, default='active')

    objects = CustomUserManager()

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

class Provider(models.Model):
    name = models.CharField(max_length=50)
    rif = models.CharField(max_length=12, unique=True)
    phone = models.CharField(max_length=12, blank=True)
    email = models.EmailField(blank=True)
    contact_name = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=20)
    min_stock = models.IntegerField(default=0)
    stock_actual = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    location = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

class PurchaseOrder(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pendiente')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

class Entrada(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.product.stock_actual += self.quantity
        self.product.save()
        super().save(*args, **kwargs)

class InventoryAdjustment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    system_qty = models.IntegerField()
    physical_qty = models.IntegerField()
    difference = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class InventarioSesion(models.Model):
    ESTADOS = (
        ('en_proceso', 'En Proceso'),
        ('finalizado', 'Finalizado'),
        ('conciliado', 'Conciliado'),
        ('cancelado', 'Cancelado'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ESTADOS, default='en_proceso')
    notas = models.TextField(blank=True)
    total_productos = models.IntegerField(default=0)
    productos_con_diferencia = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    conciliated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sesion de Inventario'
        verbose_name_plural = 'Sesiones de Inventario'


class DetalleConteo(models.Model):
    sesion = models.ForeignKey(InventarioSesion, on_delete=models.CASCADE, related_name='detalles')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_sistema = models.IntegerField()
    cantidad_contada = models.IntegerField()
    diferencia = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Detalle de Conteo'
        verbose_name_plural = 'Detalles de Conteo'
        unique_together = ['sesion', 'product']


class Salida(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salidas_registradas')
    receptor = models.CharField(max_length=200, help_text='Persona o area que recibe el producto')
    quantity = models.IntegerField()
    motivo = models.TextField(help_text='Motivo o razon de la salida')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Restar del stock al crear una salida
        if not self.pk:  # Solo al crear, no al editar
            self.product.stock_actual -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Salida'
        verbose_name_plural = 'Salidas'
        ordering = ['-created_at']
