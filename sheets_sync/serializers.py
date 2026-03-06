from rest_framework import serializers
from .models import BajaRetencion, LogCorreccion


class LogCorreccionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LogCorreccion
        fields = ['campo', 'valor_original', 'valor_corregido', 'fecha']


class BajaRetencionSerializer(serializers.ModelSerializer):
    correcciones     = LogCorreccionSerializer(many=True, read_only=True)
    total_correcciones = serializers.SerializerMethodField()

    class Meta:
        model  = BajaRetencion
        fields = [
            'id',
            'fecha',
            'cat',
            'telefono',
            'retencion_baja',
            'tipo',
            'motivo',
            'apoyo_utilizado',
            'comentarios',
            'colonia',
            'fila_sheets',
            'creado',
            'actualizado',
            'total_correcciones',
            'correcciones',
        ]

    def get_total_correcciones(self, obj):
        return obj.correcciones.count()


class BajaRetencionListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados — sin detalle de correcciones."""
    total_correcciones = serializers.SerializerMethodField()

    class Meta:
        model  = BajaRetencion
        fields = [
            'id',
            'fecha',
            'cat',
            'telefono',
            'tipo',
            'motivo',
            'colonia',
            'total_correcciones',
            'actualizado',
        ]

    def get_total_correcciones(self, obj):
        return obj.correcciones.count()


class StatsSerializer(serializers.Serializer):
    """Para el endpoint de estadísticas del dashboard."""
    total      = serializers.IntegerField()
    bajas      = serializers.IntegerField()
    retenciones = serializers.IntegerField()
    sin_colonia = serializers.IntegerField()
    correcciones_total = serializers.IntegerField()