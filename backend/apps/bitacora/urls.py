from django.urls import path
from . import views

urlpatterns = [
    path('actividades/', views.lista_actividades, name='lista_actividades'),
    path('cierres/', views.cierres_caja, name='cierres_caja'),
    path('cierres/<str:fecha>/', views.detalle_cierre, name='detalle_cierre'),
]