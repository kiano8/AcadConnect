import os
from pathlib import Path

try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass



BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-college-companion-dev-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    "https://your-project.vercel.app"
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'widget_tweaks',
    'django_apscheduler',
    # Local apps
    'apps.accounts',
    'apps.tasks',
    'apps.schedule',
    'apps.grades',
    'apps.habits',
    'apps.wellness',
    'apps.notifications',
    'apps.collaboration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = os.environ.get("DATABASE_URL")

if HAS_DJ_DATABASE_URL and DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ──────────────────────────────────────────────
# EMAIL CONFIGURATION
# In development:  console backend (prints to terminal)
# In production:   set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
#                  and fill SMTP_* vars in .env
# ──────────────────────────────────────────────
EMAIL_BACKEND    = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST       = os.getenv('SMTP_HOST', 'smtp.gmail.com')
EMAIL_PORT       = int(os.getenv('SMTP_PORT', 587))
EMAIL_USE_TLS    = True
EMAIL_HOST_USER  = os.getenv('SMTP_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASS', '')
DEFAULT_FROM_EMAIL  = os.getenv('FROM_EMAIL', 'AcadConnect <noreply@acadconnect.app>')

# ──────────────────────────────────────────────
# AUTH TOKEN SETTINGS
# ──────────────────────────────────────────────
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:8000')

# Email verification token lifetime (hours)
EMAIL_VERIFICATION_TIMEOUT_HOURS = 24

# Password reset token lifetime (minutes)
PASSWORD_RESET_TIMEOUT_MINUTES = 30

# Resend cooldown (seconds) — prevent spam
RESEND_COOLDOWN_SECONDS = 60

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25
