from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.dashboard_stats, name='dashboard_stats'),
    path('ocupacion-semanal/', views.ocupacion_semanal, name='ocupacion_semanal'),
    path('habitaciones-grid/', views.habitaciones_grid, name='habitaciones_grid'),
    path('actividades/', views.actividades_dashboard, name='actividades_dashboard'),
    path('alertas/', views.alertas_dashboard, name='alertas_dashboard'),
]