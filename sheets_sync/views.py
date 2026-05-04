from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from django.core.management import call_command
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
import io

from .models import BajaRetencion, LogCorreccion
from .serializers import (
    BajaRetencionSerializer,
    BajaRetencionListSerializer,
    LogCorreccionSerializer,
    StatsSerializer,
)


# ── Listado de registros ─────────────────────────────────────────────────────

class BajaRetencionListView(ListAPIView):
    serializer_class = BajaRetencionListSerializer

    def get_queryset(self):
        qs = BajaRetencion.objects.prefetch_related('correcciones').all()

        # Filtros opcionales por query params
        tipo    = self.request.query_params.get('tipo')
        motivo  = self.request.query_params.get('motivo')
        colonia = self.request.query_params.get('colonia')
        fecha   = self.request.query_params.get('fecha')
        search  = self.request.query_params.get('search')

        if tipo:
            qs = qs.filter(tipo__iexact=tipo)
        if motivo:
            qs = qs.filter(motivo__icontains=motivo)
        if colonia:
            qs = qs.filter(colonia__icontains=colonia)
        if fecha:
            qs = qs.filter(fecha=fecha)
        if search:
            qs = qs.filter(
                Q(telefono__icontains=search) |
                Q(cat__icontains=search)      |
                Q(colonia__icontains=search)  |
                Q(motivo__icontains=search)
            )

        return qs


# ── Detalle de un registro ───────────────────────────────────────────────────

class BajaRetencionDetailView(RetrieveAPIView):
    queryset         = BajaRetencion.objects.prefetch_related('correcciones').all()
    serializer_class = BajaRetencionSerializer


# ── Estadísticas para el dashboard ──────────────────────────────────────────

class StatsView(APIView):

    def get(self, request):
        total       = BajaRetencion.objects.count()
        bajas       = BajaRetencion.objects.filter(tipo='BAJA').count()
        retenciones = BajaRetencion.objects.filter(tipo='RETENCION').count()
        sin_colonia = BajaRetencion.objects.filter(colonia='Sin Colonia').count()
        correcciones_total = LogCorreccion.objects.count()

        # Top 5 motivos
        top_motivos = (
            BajaRetencion.objects
            .values('motivo')
            .annotate(total=Count('motivo'))
            .order_by('-total')[:5]
        )

        # Top 5 colonias
        top_colonias = (
            BajaRetencion.objects
            .exclude(colonia='Sin Colonia')
            .values('colonia')
            .annotate(total=Count('colonia'))
            .order_by('-total')[:5]
        )

        # Registros por mes (últimos 6 meses)
        from django.db.models.functions import TruncMonth
        por_mes = (
            BajaRetencion.objects
            .annotate(mes=TruncMonth('fecha'))
            .values('mes')
            .annotate(total=Count('id'))
            .order_by('mes')
            .filter(mes__isnull=False)
        )

        data = {
            'total':             total,
            'bajas':             bajas,
            'retenciones':       retenciones,
            'sin_colonia':       sin_colonia,
            'correcciones_total': correcciones_total,
            'top_motivos':       list(top_motivos),
            'top_colonias':      list(top_colonias),
            'por_mes':           [
                {
                    'mes':   r['mes'].strftime('%b %Y') if r['mes'] else '',
                    'total': r['total']
                }
                for r in por_mes
            ],
        }

        return Response(data, status=status.HTTP_200_OK)


# ── Sincronización manual ────────────────────────────────────────────────────

class SyncView(APIView):

    def post(self, request):
        try:
            # Captura el output del management command
            out = io.StringIO()
            call_command('sync_sheets', stdout=out)
            output = out.getvalue()

            return Response({
                'ok':      True,
                'mensaje': 'Sincronización completada',
                'detalle': output,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'ok':    False,
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Log de correcciones ──────────────────────────────────────────────────────

class LogCorreccionListView(ListAPIView):
    serializer_class = LogCorreccionSerializer

    def get_queryset(self):
        qs = LogCorreccion.objects.select_related('registro').all()

        # Filtrar por campo corregido
        campo = self.request.query_params.get('campo')
        if campo:
            qs = qs.filter(campo__iexact=campo)

        return qs[:100]  # máximo 100 logs recientes