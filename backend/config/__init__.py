# Indica a Django qué settings usar según variable de entorno
import os
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.dev')