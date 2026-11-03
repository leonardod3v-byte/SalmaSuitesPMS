from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import OcupacionViewSet

router = DefaultRouter()
router.register(r'ocupaciones', OcupacionViewSet, basename='ocupacion')

urlpatterns = [
    path('configuracion-general/', views.configuracion_general, name='configuracion_general'),
    path('', include(router.urls)),
]
