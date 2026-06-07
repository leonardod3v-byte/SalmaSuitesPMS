from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservas_list, name='reservas_list'),
    path('<int:pk>/', views.reserva_detail, name='reserva_detail'),
    path('<int:pk>/no-show/', views.registrar_no_show, name='registrar_no_show'),
    path('<int:pk>/checkin/', views.ejecutar_checkin, name='ejecutar_checkin'),
    path('<int:pk>/checkout/', views.ejecutar_checkout, name='ejecutar_checkout'),
    path('<int:pk>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    path('<int:pk>/consumo/', views.agregar_consumo, name='agregar_consumo'),
    path('<int:pk>/cambiar-habitacion/', views.cambiar_habitacion, name='cambiar_habitacion'),
    path('actividades/', views.actividades_recientes, name='actividades_recientes'),
]