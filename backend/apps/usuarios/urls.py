from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),
    path('password-reset/request/', views.request_password_reset, name='password_reset_request'),
    path('password-reset/verify/', views.verify_reset_code, name='password_reset_verify'),
    path('password-reset/reset/', views.reset_password, name='password_reset'),
    path('usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/<int:pk>/', views.gestion_usuario_individual, name='gestion_usuario_individual'),
    path('usuarios/<int:pk>/actividad/', views.actividad_usuario, name='actividad_usuario'),
]