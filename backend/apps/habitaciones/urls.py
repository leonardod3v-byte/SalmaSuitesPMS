from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_habitaciones, name='lista_habitaciones'),
    path('<int:pk>/', views.detalle_habitacion, name='detalle_habitacion'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_habitacion, name='cambiar_estado'),
    path('<int:pk>/disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),
    path('disponibles/', views.listar_disponibles_view, name='listar_disponibles'),
]