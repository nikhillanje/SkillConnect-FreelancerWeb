"""
Django settings for SkillConnect project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ===============================
# Paths and Security
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")  # keep fallback for safety

# Turn off DEBUG for production
DEBUG = False

# Add your Render domain here (and localhost for testing)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'skillconnect-freelancerweb.onrender.com']

# ===============================
# Application Definition
# ===============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'SkillConnected',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    #Add WhiteNoise for serving static files on Render
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SkillConnect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'SkillConnect.wsgi.application'

# ===============================
# Database (SQLite)
# ===============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===============================
# Password Validation
# ===============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===============================
# Internationalization
# ===============================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===============================
# Static and Media Files
# ===============================

# Static files settings for Render
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # where collectstatic will store files
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# WhiteNoise settings for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media (if any)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ===============================
# Miscellaneous
# ===============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGOUT_REDIRECT_URL = '/'

# ===============================
# Email Settings
# ===============================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# ===============================
# Gemini API Key
# ===============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ===============================
# Session Settings
# ===============================
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
