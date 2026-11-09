from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OcupacionViewSet

router = DefaultRouter()
router.register(r'ocupaciones', OcupacionViewSet, basename='ocupacion')

urlpatterns = [
    path('', include(router.urls)),
]
