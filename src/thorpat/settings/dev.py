from .base import *  # noqa: F401, F403

ALLOWED_HOSTS = ["*"]
MIDDLEWARE = [
    # "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "thorpat.core.middleware.CartMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # "django_prometheus.middleware.PrometheusAfterMiddleware",
]
SITE_ID = 1
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ["http://*"]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

LOGIN_REDIRECT_URL = "/"

STATICFILES_DIRS = [
    BASE_DIR / "static",  # If your static folder is at src/static/
]
STATIC_ROOT = BASE_DIR.parent / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "mediafiles"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

PASSWORD_RESET_TIMEOUT = 3600

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)
