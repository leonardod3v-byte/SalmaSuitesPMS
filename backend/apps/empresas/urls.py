from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_empresas, name='lista_empresas'),
    path('<int:pk>/', views.detalle_empresa, name='detalle_empresa'),
]
