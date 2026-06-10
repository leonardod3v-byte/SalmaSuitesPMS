from django.urls import path
from . import views

urlpatterns = [
    # CRUD de reservaciones
    path('', views.lista_reservaciones, name='lista_reservaciones'),
    path('<int:pk>/', views.detalle_reservacion, name='detalle_reservacion'),
    # Acciones
    path('<int:pk>/checkin/', views.checkin_reservacion, name='checkin_reservacion'),
    path('<int:pk>/checkout/', views.checkout_reservacion, name='checkout_reservacion'),
    path('<int:pk>/cancelar/', views.cancelar_reservacion, name='cancelar_reservacion'),
    path('<int:pk>/noshow/', views.noshow_reservacion, name='noshow_reservacion'),
    path('<int:pk>/resumen-checkout/', views.resumen_checkout, name='resumen_checkout'),
    # Consumos asociados a una reservación
    path('<int:pk>/consumos/', views.consumos_reservacion, name='consumos_reservacion'),
    # Pagos asociados a una reservación (lista y creación)
    path('<int:pk>/pagos/', views.pagos_reservacion, name='pagos_reservacion'),
]