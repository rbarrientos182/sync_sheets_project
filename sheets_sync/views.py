from rest_framework.decorators import api_view
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
)


# ── Listado de registros ─────────────────────────────────────────────────────

@api_view(['GET'])
def registros_list(request):
    qs = BajaRetencion.objects.prefetch_related('correcciones').all()

    # Filtros opcionales
    tipo    = request.query_params.get('tipo')
    motivo  = request.query_params.get('motivo')
    colonia = request.query_params.get('colonia')
    fecha   = request.query_params.get('fecha')
    search  = request.query_params.get('search')

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

    serializer = BajaRetencionListSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ── Detalle de un registro ───────────────────────────────────────────────────

@api_view(['GET'])
def registros_detail(request, pk):
    try:
        registro = BajaRetencion.objects.prefetch_related('correcciones').get(pk=pk)
    except BajaRetencion.DoesNotExist:
        return Response(
            {'error': 'Registro no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = BajaRetencionSerializer(registro)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ── Estadísticas para el dashboard ──────────────────────────────────────────

@api_view(['GET'])
def stats(request):
    total              = BajaRetencion.objects.count()
    bajas              = BajaRetencion.objects.filter(tipo='BAJA').count()
    retenciones        = BajaRetencion.objects.filter(tipo='RETENCION').count()
    sin_colonia        = BajaRetencion.objects.filter(colonia='Sin Colonia').count()
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

    # Registros por mes
    por_mes = (
        BajaRetencion.objects
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
        .filter(mes__isnull=False)
    )

    data = {
        'total':              total,
        'bajas':              bajas,
        'retenciones':        retenciones,
        'sin_colonia':        sin_colonia,
        'correcciones_total': correcciones_total,
        'top_motivos':        list(top_motivos),
        'top_colonias':       list(top_colonias),
        'por_mes': [
            {
                'mes':   r['mes'].strftime('%b %Y') if r['mes'] else '',
                'total': r['total']
            }
            for r in por_mes
        ],
    }

    return Response(data, status=status.HTTP_200_OK)


# ── Sincronización manual ────────────────────────────────────────────────────

@api_view(['POST'])
def sync(request):
    try:
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

@api_view(['GET'])
def logs_list(request):
    qs = LogCorreccion.objects.select_related('registro').all()

    campo = request.query_params.get('campo')
    if campo:
        qs = qs.filter(campo__iexact=campo)

    serializer = LogCorreccionSerializer(qs[:100], many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)