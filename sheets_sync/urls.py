from django.urls import path
from . import views

urlpatterns = [
    # Listado y detalle
    path('registros/',         views.BajaRetencionListView.as_view(),   name='registros-list'),
    path('registros/<int:pk>/', views.BajaRetencionDetailView.as_view(), name='registros-detail'),

    # Estadísticas para el dashboard
    path('stats/',             views.StatsView.as_view(),               name='stats'),

    # Trigger manual de sincronización
    path('sync/',              views.SyncView.as_view(),                name='sync'),

    # Log de correcciones
    path('logs/',              views.LogCorreccionListView.as_view(),   name='logs-list'),
]