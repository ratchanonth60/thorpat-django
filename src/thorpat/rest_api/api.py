from django.conf import settings
from ninja import NinjaAPI
from ninja.errors import AuthenticationError, HttpError

from thorpat.rest_api.exception_handlers import (
    http_exception_handler,
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
app.add_exception_handler(AuthenticationError, http_exception_handler_auth)  # type: ignore
app.add_exception_handler(Exception, http_exception_handler_500)  # type: ignore
