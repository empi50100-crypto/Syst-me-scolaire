from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("La variable d'environnement SECRET_KEY doit être définie")

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

hostname = os.getenv('HOSTNAME', '')
try:
    local_ip = __import__('socket').gethostbyname(__import__('socket').gethostname())
except:
    local_ip = '127.0.0.1'

# Configuration ALLOWED_HOSTS - en production, spécifier explicitement les domaines
if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', local_ip]
else:
    allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '')
    if allowed_hosts_env:
        ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',')]
    else:
        ALLOWED_HOSTS = ['127.0.0.1', 'localhost', local_ip]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'channels',
    'authentification',
    'scolarite',
    'enseignement',
    'presences',
    'finances',
    'rapports',
    'ressources_humaines',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.ActiveAnneeMiddleware',
    'core.middleware.SessionTimeoutMiddleware',
]

# Configuration CSRF - Production: désactiver CSRF_ALLOW_ALL_ORIGINS
CSRF_ALLOW_ALL_ORIGINS = os.getenv('CSRF_ALLOW_ALL_ORIGINS', 'False').lower() in ('true', '1', 'yes')

# Origines de confiance pour CSRF
CSRF_TRUSTED_ORIGINS_ENV = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if CSRF_TRUSTED_ORIGINS_ENV:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_ENV.split(',')]
else:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'https://localhost:8000',
        'https://127.0.0.1:8000',
    ]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.annee_scolaire_actuelle',
                'core.context_processors.notification_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'gestion_scolaire'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Vérification que le mot de passe DB est défini en production
if not DEBUG and not DATABASES['default']['PASSWORD']:
    raise ValueError("La variable DB_PASSWORD doit être définie en production")

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'authentification:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'authentification:login'

AUTH_USER_MODEL = 'authentification.Utilisateur'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Rate limiting pour protéger contre les abus d'API
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',    # Limite pour utilisateurs non authentifiés
        'user': '1000/hour',   # Limite pour utilisateurs authentifiés
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Protection contre les attaques par brute-force
AXES_ENABLED = os.getenv('AXES_ENABLED', 'True').lower() in ('true', '1', 'yes')
AXES_FAILURE_LIMIT = int(os.getenv('AXES_FAILURE_LIMIT', '5'))  # 5 tentatives max
AXES_COOLOFF_TIME = timedelta(minutes=int(os.getenv('AXES_COOLOFF_TIME_MINUTES', '30')))  # 30 min de blocage
AXES_RESET_ON_SUCCESS = True  # Réinitialiser le compteur après connexion réussie

# Configuration CORS - Production: désactiver CORS_ALLOW_ALL_ORIGINS
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False').lower() in ('true', '1', 'yes')
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS_ENV = os.getenv('CORS_ALLOWED_ORIGINS', '')
if CORS_ALLOWED_ORIGINS_ENV:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS_ENV.split(',')]
else:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'https://localhost:8000',
        'https://127.0.0.1:8000',
    ]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Configuration des cookies de session et CSRF
# En production: toujours utiliser HTTPS pour les cookies
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG  # True en production (HTTPS requis)
CSRF_COOKIE_SAMESITE = 'Strict'

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG  # True en production (HTTPS requis)
SESSION_COOKIE_SAMESITE = 'Strict'

# HSTS - Force HTTPS
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1 an en production
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = not DEBUG

# Redirection forcée vers HTTPS en production
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configuration SMTP pour Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Vérification des credentials email en production
if not DEBUG and EMAIL_HOST_USER and not EMAIL_HOST_PASSWORD:
    import warnings
    warnings.warn("EMAIL_HOST_PASSWORD non défini - l'envoi d'emails échouera")

logs_dir = BASE_DIR / 'logs'
logs_dir.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': logs_dir / 'security.log',
        },
    },
    'loggers': {
        'axes': {'handlers': ['file'], 'level': 'INFO', 'propagate': False},
        'django.security': {'handlers': ['file'], 'level': 'INFO', 'propagate': False},
    },
}

ASGI_APPLICATION = 'core.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
