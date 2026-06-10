import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Cargar variables de entorno desde .env ─────────────────────────────────
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
    'corsheaders',

    # Apps del proyecto
    'apps.usuarios',
    'apps.huespedes',
    'apps.habitaciones',
    'apps.reservaciones',
    'apps.inventario',
    'apps.dashboard',
    'apps.reportes',
    'apps.bitacora',
    'apps.configuracion',
]

# ── Middleware ─────────────────────────────────────────────────────────────
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
AUTH_USER_MODEL = 'usuarios.User'

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
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.usuarios.authentication.CookieTokenAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ── CORS ───────────────────────────────────────────────────────────────────
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
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# ── Cookies de sesión ──────────────────────────────────────────────────────
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE   = False  # True solo en producción con HTTPS
CSRF_COOKIE_SAMESITE    = 'Lax'
CSRF_COOKIE_SECURE      = False  # True solo en producción con HTTPS


# ── Cookie de autenticación ────────────────────────────────────────────────
AUTH_TOKEN_COOKIE_NAME = 'auth_token'
AUTH_TOKEN_COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 días

# ── Email (Gmail SMTP) ─────────────────────────────────────────────────────
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
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# ── Caché ──────────────────────────────────────────────────────────────────
# En desarrollo: memoria local (sin dependencias extra)
# En producción: cambiar a Redis con django-redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'salmasuite-cache',
    }
}

# Cuando tengas Redis en producción, reemplaza por:
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#         'OPTIONS': { 'CLIENT_CLASS': 'django_redis.client.DefaultClient' },
#     }
# }