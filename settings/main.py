import sys

from .base import *

INSTALLED_APPS += [
    'apps',
    'django_extensions',
    'cacheops',
    'corsheaders',
    'rest_framework',
    'channels',
]

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

# Environment
TESTING_ENVIRONMENT = 'testing'
PRODUCTION_ENVIRONMENT = 'production'
STAGING_ENVIRONMENT = 'staging'
DEVELOPMENT_ENVIRONMENT = 'development'

if 'test' in sys.argv:  # noqa: SIM108
    ENVIRONMENT = TESTING_ENVIRONMENT
else:
    ENVIRONMENT = env('ENVIRONMENT')

# Cacheops
# https://github.com/Suor/django-cacheops
CACHEOPS_REDIS = f"{env('REDIS_URL')}/1"
CACHEOPS_DEFAULTS = {'timeout': 60 * 60}
CACHEOPS = {
    'auth.user': {'ops': 'get', 'timeout': 60 * 15},
    'auth.*': {'ops': ('fetch', 'get')},
    'auth.permission': {'ops': 'all'},
    '*.*': {},
}

# Testing environment optimizations
if ENVIRONMENT == TESTING_ENVIRONMENT:
    CELERY_TASK_ALWAYS_EAGER = True

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/(api|ws)/?.*$'

# Channels Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'crypto_service.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'apps': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
