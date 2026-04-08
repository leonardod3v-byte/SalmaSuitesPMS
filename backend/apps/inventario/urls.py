from django.urls import path
from . import views

urlpatterns = [
    path('', views.productos_list, name='productos_list'),
    path('<int:pk>/', views.producto_detail, name='producto_detail'),
    path('<int:pk>/entrada/', views.entrada_stock, name='entrada_stock'),
    path('<int:pk>/ajuste/', views.ajuste_stock, name='ajuste_stock'),
    path('alertas/', views.alertas_stock, name='alertas_stock'),
]