from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_huespedes, name='lista_huespedes'),
    path('exportar/', views.exportar_huespedes_xls, name='exportar_huespedes_xls'),
    path('<int:pk>/', views.detalle_huesped, name='detalle_huesped'),
    path('<int:pk>/disponibilidad/', views.validar_disponibilidad, name='validar_disponibilidad'),
]