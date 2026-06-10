from django.urls import path
from . import views

urlpatterns = [
    path('diario/', views.detalle_diario, name='detalle_diario'),
    path('ingresos/', views.ingresos_periodo, name='ingresos_periodo'),
]