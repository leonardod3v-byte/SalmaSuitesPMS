from django.urls import path
from . import views

urlpatterns = [
    path('consumos/<int:huesped_id>/', views.reporte_consumos_huesped, name='reporte_consumos'),
    path('reservas/', views.reporte_reservas_activas, name='reporte_reservas'),
    path('ingresos/', views.reporte_ingresos, name='reporte_ingresos'),
    path('historial/', views.historial_reportes, name='historial_reportes'),
]