from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.productos_lista, name='productos_lista'),
    path('productos/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('movimientos/', views.movimientos_lista, name='movimientos_lista'),
    path('entradas/', views.registrar_entrada_view, name='registrar_entrada'),
    path('ajustes/', views.registrar_ajuste_view, name='registrar_ajuste'),
    path('alertas/bajos/', views.productos_bajos_count, name='productos_bajos_count'),
]