from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagos_list, name='pagos_list'),
    path('resumen-hoy/', views.resumen_pagos_hoy, name='resumen_pagos_hoy'),
    path('cierre/', views.generar_cierre_caja, name='generar_cierre_caja'),
    path('cierres/', views.historial_cierres, name='historial_cierres'),
]