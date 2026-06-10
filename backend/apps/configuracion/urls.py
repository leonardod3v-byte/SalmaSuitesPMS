from django.urls import path
from . import views

urlpatterns = [
    path('', views.configuracion_general, name='configuracion_general'),
    path('colores-clientes/', views.colores_tipo_cliente, name='colores_tipo_cliente'),
    path('colores-estados/', views.colores_estado_habitacion, name='colores_estado_habitacion'),
]