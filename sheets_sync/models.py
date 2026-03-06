from django.db import models

class BajaRetencion(models.Model):

    TIPO_CHOICES = [
        ('BAJA', 'Baja'),
        ('RETENCION', 'Retención'),
    ]

    MOTIVO_CHOICES = [
        ('CALIDAD DE SERVICIO',            'Calidad de Servicio'),
        ('CAMBIO DE COMPANIA',             'Cambio de Compañía'),
        ('CAMBIO DE RESIDENCIA',           'Cambio de Residencia'),
        ('CAMBIO RESIDENCIA ZONA SIN RED', 'Cambio Residencia Zona Sin Red'),
        ('CARGOS NO RECONOCIDOS',          'Cargos No Reconocidos'),
        ('CIERRE DE NEGOCIO',              'Cierre de Negocio'),
        ('DEFUNCION',                      'Defunción'),
        ('ECONOMIA',                       'Economía'),
        ('ESCALACION DE QUEJA',            'Escalación de Queja'),
        ('FACTURACION',                    'Facturación'),
        ('OFERTA COMERCIAL',               'Oferta Comercial'),
        ('OFERTA DE LA COMPETENCIA',       'Oferta de la Competencia'),
        ('REESTRUCTURA CUENTA MAESTRA',    'Reestructura Cuenta Maestra'),
        ('REVENTA',                        'Reventa'),
    ]

    fecha           = models.DateField(null=True, blank=True)
    cat             = models.CharField(max_length=100, blank=True)
    telefono        = models.CharField(max_length=20, blank=True, db_index=True)
    retencion_baja  = models.CharField(max_length=20, blank=True)
    tipo            = models.CharField(max_length=20, choices=TIPO_CHOICES, blank=True)
    motivo          = models.CharField(max_length=50, choices=MOTIVO_CHOICES, blank=True)
    apoyo_utilizado = models.CharField(max_length=255, blank=True)
    comentarios     = models.TextField(blank=True)
    colonia         = models.CharField(max_length=150, default='Sin Colonia')
    fila_sheets     = models.IntegerField(null=True, blank=True)
    creado          = models.DateTimeField(auto_now_add=True)
    actualizado     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Baja / Retención'
        verbose_name_plural = 'Bajas y Retenciones'
        ordering            = ['-fecha']
        # evita duplicados por teléfono + fecha
        unique_together     = [['telefono', 'fecha']]

    def __str__(self):
        return f"{self.telefono} | {self.tipo} | {self.fecha}"


class LogCorreccion(models.Model):
    registro        = models.ForeignKey(
                        BajaRetencion,
                        on_delete=models.CASCADE,
                        related_name='correcciones'
                      )
    campo           = models.CharField(max_length=100)
    valor_original  = models.TextField()
    valor_corregido = models.TextField()
    fecha           = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Log de Corrección'
        verbose_name_plural = 'Logs de Correcciones'
        ordering            = ['-fecha']

    def __str__(self):
        return f"{self.campo}: '{self.valor_original}' → '{self.valor_corregido}'"
