from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.contrib.auth import get_user_model

def health_check(request):
    try:
        # Consulta ligera a Supabase usando el modelo de usuario activo
        User = get_user_model()
        User.objects.exists()
        return JsonResponse({"status": "ok", "database": "connected"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "details": str(e)}, status=500)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
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