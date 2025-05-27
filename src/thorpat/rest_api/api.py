from ninja import NinjaAPI
from ninja.errors import HttpError

from thorpat.rest_api.exception_handlers import http_exception_handler

from .v1 import users

app = NinjaAPI(title="Thorpat API", version="1.0.0", csrf=True)
app.add_router("/v1/users/", users.router)
app.add_exception_handler(HttpError, http_exception_handler)
