from django.urls import path
from .views import registros_list, registros_detail, stats, sync, logs_list
urlpatterns = [
    # Listado y detalle
    path('registros/',registros_list, name='registros-list'),
    path('registros/<int:pk>/', registros_detail, name='registros-detail'),

    # Estadísticas para el dashboard
    path('stats/', stats, name='stats'),

    # Trigger manual de sincronización
    path('sync/', sync, name='sync'),

    # Log de correcciones
    path('logs/',logs_list, name='logs-list'),
]