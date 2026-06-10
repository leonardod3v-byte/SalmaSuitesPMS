from django.urls import path
from . import views

urlpatterns = [
    path('kpis/', views.kpis, name='kpis'),
    path('ocupacion-semanal/', views.ocupacion_semanal, name='ocupacion_semanal'),
    path('proximos-checkouts/', views.proximos_checkouts, name='proximos_checkouts'),
]