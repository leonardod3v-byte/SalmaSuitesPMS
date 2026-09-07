from django.urls import path
from . import views

urlpatterns = [
    path('diario/', views.detalle_diario, name='detalle_diario'),
    path('ingresos/', views.ingresos_periodo, name='ingresos_periodo'),
    path('hoja-huesped/<int:reserva_id>/', views.hoja_huesped_pdf, name='hoja_huesped_pdf'),
    path('registro-reservaciones/', views.registro_reservaciones_pdf, name='registro_reservaciones_pdf'),
    path('cierre-caja-pdf/', views.cierre_caja_pdf, name='cierre_caja_pdf'),
]