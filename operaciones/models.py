from django.db import models
from django.core.exceptions import ValidationError


class Producto(models.Model):
    CATEGORIA_CHOICES = [
        ('SOLIDO', 'Sólido'),
        ('LIQUIDO', 'Líquido'),
    ]

    ESTADO_CHOICES = [
        ('ALTO', 'Stock Alto'),
        ('MEDIO', 'Stock Medio'),
        ('BAJO', 'Stock Bajo'),
    ]

    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código del Producto",
        help_text="Código único identificador del producto (SKU)"
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name="Descripción"
    )
    unidad = models.CharField(
        max_length=50,
        verbose_name="Unidad / Presentación",
        help_text="Ej: SACOS 55 LBS, TAMBOR 55 GLS, TOTE"
    )
    libraje = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.0,
        verbose_name="Libraje (LBS)",
        help_text="Peso o libraje unitario en libras"
    )
    gravedad = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=1.0,
        verbose_name="Gravedad Específica"
    )
    costo = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0.0,
        verbose_name="Costo Unitario ($)"
    )
    cantidad = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0.0,
        verbose_name="Cantidad (Stock)"
    )
    categoria = models.CharField(
        max_length=10,
        choices=CATEGORIA_CHOICES,
        default='SOLIDO',
        verbose_name="Categoría"
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='ALTO',
        verbose_name="Estado de Stock"
    )
    observacion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observación"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto de Inventario"
        verbose_name_plural = "Productos de Inventario"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    def clean(self):
        # Normalizar código
        if self.codigo:
            self.codigo = self.codigo.strip()
            # Validar unicidad insensible a mayúsculas
            qs = Producto.objects.filter(codigo__iexact=self.codigo)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({"codigo": f"Ya existe un producto registrado con el código '{self.codigo}'."})

        if self.cantidad is not None and self.cantidad < 0:
            raise ValidationError({"cantidad": "La cantidad no puede ser negativa."})

        # Cálculo automático del estado
        self.estado = self.calcular_estado_automatico()

    def save(self, *args, **kwargs):
        self.estado = self.calcular_estado_automatico()
        super().save(*args, **kwargs)

    def calcular_estado_automatico(self):
        """
        Regla de negocio:
        0 a 20: Stock Bajo
        21 a 50: Stock Medio
        > 50: Stock Alto
        """
        cant = float(self.cantidad or 0)
        if cant <= 20:
            return 'BAJO'
        elif cant <= 50:
            return 'MEDIO'
        return 'ALTO'

    def to_dict(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "unidad": self.unidad,
            "libraje": float(self.libraje),
            "gravedad": float(self.gravedad),
            "costo": float(self.costo),
            "cantidad": float(self.cantidad),
            "categoria": self.categoria,
            "categoria_display": self.get_categoria_display(),
            "estado": self.estado,
            "estado_display": self.get_estado_display(),
            "observacion": self.observacion or "",
            "puede_eliminar": self.cantidad == 0,
        }
