from django.urls import path
from . import views

urlpatterns = [
    path('', views.huespedes_list, name='huespedes_list'),
    path('<int:pk>/', views.huesped_detail, name='huesped_detail'),
    path('buscar/', views.buscar_huesped_por_documento, name='buscar_huesped'),
]