from .celery import app as celery_app

__all__ = ("celery_app",)

APPS_BASE = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

APPS = [
    "thorpat.apps.users",
    "thorpat.apps.profiles",
]

APPS_THIRD_PARTY = [
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    # "rest_framework",
    "rest_framework_simplejwt",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # "django_prometheus",
    "django_typer",
    "django_countries",
    "phonenumber_field",
]
