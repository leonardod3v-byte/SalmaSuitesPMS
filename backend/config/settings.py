import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Cargar variables de entorno desde .env ─────────────────────────────────
# Se hace antes de cualquier otra configuración para que todas
# las variables estén disponibles desde el inicio
env_path = BASE_DIR / '.env'
if env_path.exists():
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

# ── Seguridad base ─────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY') or '49(2lnui!j3w39=xg(g-n)_4dns_zs%8wj-t_m!@drg@z=xok&'
DEBUG      = os.environ.get('DEBUG', 'True') == 'True'

# ── Hosts permitidos ───────────────────────────────────────────────────────
# En desarrollo se permite cualquier host para simplificar la configuración
# En producción debe listarse explícitamente el dominio del servidor
ALLOWED_HOSTS = ['*'] if DEBUG else []

# ── Aplicaciones instaladas ────────────────────────────────────────────────
# Primero las de Django, luego terceros, luego las propias del proyecto
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',

    # Apps del proyecto
    'apps.users',
    'apps.habitaciones',
    'apps.guests',
    'apps.reservaciones',
    'apps.pagos',
    'apps.inventario',
    'apps.dashboard',
    'apps.reportes',
    'apps.notificaciones',
]

# ── Middleware ─────────────────────────────────────────────────────────────
# CorsMiddleware debe ir primero para manejar los preflight OPTIONS
# antes de que cualquier otro middleware procese el request
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF      = 'config.urls'
WSGI_APPLICATION  = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ── Base de datos ──────────────────────────────────────────────────────────
# SQLite para desarrollo local por su simplicidad y bajo consumo de recursos
# Cambiar a PostgreSQL/Supabase en producción usando variables de entorno
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.parent / 'database' / 'db.sqlite3',
    }
}

# ── Modelo de usuario personalizado ───────────────────────────────────────
# Debe declararse antes de la primera migración y no cambiarse después
AUTH_USER_MODEL = 'users.User'

# ── Internacionalización ───────────────────────────────────────────────────
LANGUAGE_CODE = 'es-ve'
TIME_ZONE     = 'America/Caracas'
USE_I18N      = True
USE_TZ        = True

# ── Archivos estáticos y media ─────────────────────────────────────────────
STATIC_URL  = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = 'media/'
MEDIA_ROOT  = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Django REST Framework ──────────────────────────────────────────────────
# Se usa una clase de autenticación personalizada que exime la verificación
# CSRF para permitir que el frontend SvelteKit consuma la API sin necesidad
# de manejar tokens CSRF manualmente en cada request
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ── CORS ───────────────────────────────────────────────────────────────────
# Permite que el frontend en localhost:5173 consuma la API en localhost:8000
# CORS_ALLOW_CREDENTIALS es necesario para que las cookies de sesión
# se envíen en los requests cross-origin
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS   = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ── CSRF ───────────────────────────────────────────────────────────────────
# Los orígenes de confianza son necesarios aunque usemos CsrfExempt
# porque Django los verifica en algunas situaciones adicionales
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# ── Cookies de sesión ──────────────────────────────────────────────────────
# SameSite=Lax permite que las cookies se envíen en navegación
# cross-origin sin requerir HTTPS en desarrollo
SESSION_COOKIE_DOMAIN = None  # Dejar en None para desarrollo local
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE   = False  # True solo en producción con HTTPS
CSRF_COOKIE_SAMESITE    = 'Lax'
CSRF_COOKIE_SECURE      = False  # True solo en producción con HTTPS

# ── Email (Gmail SMTP) ─────────────────────────────────────────────────────
# Usado para enviar códigos de recuperación de contraseña (RF01)
# Las credenciales se cargan desde .env para no exponerlas en el código
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'Sistema PMS Hotel Salma Suite VIP <noreply@salmasuite.com>'
)

# ── Simple JWT ─────────────────────────────────────────────────────────────
# Usado para generar tokens temporales en el flujo de recuperación
# de contraseña. Access token de corta duración por seguridad
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}