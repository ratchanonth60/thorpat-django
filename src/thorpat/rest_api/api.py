from django.conf import settings
from django.http import Http404
from ninja import NinjaAPI
from ninja.errors import AuthenticationError, HttpError, ValidationError

from thorpat.rest_api.exception_handlers import (
    http_exception_handler,
    http_exception_handler_404,
    http_exception_handler_422,
    http_exception_handler_500,
    http_exception_handler_auth,
)

from .auth import JWTAuth
from .v1 import router

app = NinjaAPI(
    **settings.NINJA_SETTINGS,
    auth=JWTAuth(),
)
app.add_router("/v1/", router.v1)
app.add_exception_handler(HttpError, http_exception_handler)  # type: ignore
app.add_exception_handler(Http404, http_exception_handler_404)  # type: ignore
app.add_exception_handler(AuthenticationError, http_exception_handler_auth)  # type: ignore
app.add_exception_handler(Exception, http_exception_handler_500)  # type: ignore
app.add_exception_handler(ValidationError, http_exception_handler_422)  # type: ignore
