from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.usuarios.urls')),
    path('api/habitaciones/', include('apps.habitaciones.urls')),
    path('api/huespedes/', include('apps.huespedes.urls')),
    path('api/reservaciones/', include('apps.reservaciones.urls')),
    path('api/inventario/', include('apps.inventario.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/reportes/', include('apps.reportes.urls')),
    path('api/bitacora/', include('apps.bitacora.urls')),
    path('api/configuracion/', include('apps.configuracion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass