import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# NAS local storage root
NAS_STORAGE_ROOT = os.path.join(BASE_DIR, "NAS_STORAGE")

# ── Security ───────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-dev-only-change-before-any-real-deployment"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# Add your PC's LAN IP via the env var, e.g.:
#   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.x.x
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1,192.168.1.35"
).split(",")

# ── Applications ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'accounts',
    'media_manager',
]

AUTH_USER_MODEL = 'accounts.User'

# ── REST Framework ─────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/min',
        'user': '200/min',
        'login': '5/min',
    },
}

# ── CORS — restrict to Angular dev server only ─────────────────────────────
# Add your LAN origin via env var, e.g.:
#   CORS_ALLOWED_ORIGINS=http://localhost:4200,http://192.168.x.x:4200
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:4200,http://192.168.1.35:4200"
).split(",")

# ── Upload limits ──────────────────────────────────────────────────────────
MAX_UPLOAD_SIZE_MB = 500
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif",
    "image/webp", "image/heic", "image/heif",
    "video/mp4", "video/quicktime", "video/x-msvideo",
}

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

ROOT_URLCONF = 'nas_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nas_server.wsgi.application'

# ── Database ───────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Password validation ────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Logging ────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '[{levelname}] {asctime} {module}: {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'},
    },
    'loggers': {
        'accounts': {'handlers': ['console'], 'level': 'INFO'},
        'media_manager': {'handlers': ['console'], 'level': 'INFO'},
    },
}

# ── Internationalisation ───────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
