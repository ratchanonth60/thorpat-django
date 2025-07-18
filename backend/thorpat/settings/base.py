"""
Django settings for thorpat project.

Generated by 'django-admin startproject' using Django 3.2.20.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from django.urls import reverse_lazy

from thorpat import APPS, APPS_BASE, APPS_THIRD_PARTY

from .db import *  # noqa: F401, F403

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = []
AUTH_USER_MODEL = "users.User"
SITE_ID = 1

# Application definition
INSTALLED_APPS = APPS_BASE + APPS + APPS_THIRD_PARTY


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "thorpat.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "thorpat.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",  # If your static folder is at src/static/
]
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


INSTALLED_APPS = APPS_BASE + APPS + APPS_THIRD_PARTY + [
    'drf_yasg',
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "thorpat.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "thorpat.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",  # If your static folder is at src/static/
]
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'ALLOWED_VERSIONS': ('v1',),
    'DEFAULT_VERSION': 'v1',
    'VERSION_PARAM': 'version',
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    }
}
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)  # For development
EMAIL_HOST = os.environ.get("MAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("MAIL_PORT", 25))
EMAIL_USE_TLS = os.environ.get("MAIL_STARTTLS", 1)
EMAIL_HOST_USER = os.environ.get("MAIL_USERNAME", "")
EMAIL_HOST_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("MAIL_FROM", "webmaster@localhost")

SITE_BASE_URL = os.environ.get("DJANGO_SITE_BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.environ.get(
    "FRONTEND_URL", "http://localhost:8000"
)  # Default fallback

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://redis:6379/0"
)  # ถ้าต้องการเก็บผลลัพธ์ task
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE  # ใช้ TIME_ZONE ของ Django
CELERY_TASK_TRACK_STARTED = True
CACHEOPS_REDIS = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

CACHEOPS_DEFAULTS = {"timeout": 60 * 60}
CACHEOPS = {
    "auth.user": {"ops": "get", "timeout": 60 * 15},
    "auth.*": {"ops": ("fetch", "get")},
    "auth.permission": {"ops": "all"},
    "*.*": {},
}
SITE_ID = 1
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("CLIENT_ID"),
            "secret": os.environ.get("CLIENT_SECRET"),
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "VERIFIED_EMAIL": True,
        "OAUTH_PKCE_ENABLED": True,
        "FETCH_USERINFO": True,
    },
}

SOCIALACCOUNT_LOGIN_ON_GET = True

LOGIN_REDIRECT_URL = reverse_lazy("dashboard:user_info")
LOGIN_URL = "account_login"
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True  # (Default is True, good to be explicit)
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy("home")

EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)  # For development
EMAIL_HOST = os.environ.get("MAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("MAIL_PORT", 25))
EMAIL_USE_TLS = os.environ.get("MAIL_STARTTLS", 1)
EMAIL_HOST_USER = os.environ.get("MAIL_USERNAME", "")
EMAIL_HOST_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("MAIL_FROM", "webmaster@localhost")

SITE_BASE_URL = os.environ.get("DJANGO_SITE_BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.environ.get(
    "FRONTEND_URL", "http://localhost:8000"
)  # Default fallback

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://redis:6379/0"
)  # ถ้าต้องการเก็บผลลัพธ์ task
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE  # ใช้ TIME_ZONE ของ Django
CELERY_TASK_TRACK_STARTED = True
CACHEOPS_REDIS = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

CACHEOPS_DEFAULTS = {"timeout": 60 * 60}
CACHEOPS = {
    "auth.user": {"ops": "get", "timeout": 60 * 15},
    "auth.*": {"ops": ("fetch", "get")},
    "auth.permission": {"ops": "all"},
    "*.*": {},
}
SITE_ID = 1
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("CLIENT_ID"),
            "secret": os.environ.get("CLIENT_SECRET"),
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "VERIFIED_EMAIL": True,
        "OAUTH_PKCE_ENABLED": True,
        "FETCH_USERINFO": True,
    },
}

SOCIALACCOUNT_LOGIN_ON_GET = True

LOGIN_REDIRECT_URL = reverse_lazy("dashboard:user_info")
LOGIN_URL = "account_login"
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True  # (Default is True, good to be explicit)
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy("home")
