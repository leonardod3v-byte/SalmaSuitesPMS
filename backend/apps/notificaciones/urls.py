from django.urls import path
from . import views

urlpatterns = [
    path('', views.notificaciones_list, name='notificaciones_list'),
    path('reserva/<int:reserva_id>/', views.enviar_notificacion_reserva, name='enviar_notificacion_reserva'),
    path('personalizada/', views.enviar_notificacion_personalizada, name='enviar_notificacion_personalizada'),
    path('recordatorios/', views.procesar_recordatorios_automaticos, name='procesar_recordatorios'),
]