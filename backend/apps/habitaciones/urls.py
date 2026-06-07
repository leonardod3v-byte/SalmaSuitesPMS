from django.urls import path
from . import views

urlpatterns = [
    path('', views.habitaciones_list, name='habitaciones_list'),
    path('<int:pk>/', views.habitacion_detail, name='habitacion_detail'),
    path('tipos/', views.tipos_habitacion_list, name='tipos_habitacion_list'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_limpieza, name='cambiar_estado'),
]