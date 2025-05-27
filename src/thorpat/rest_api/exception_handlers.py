from django.http import HttpResponse
from ninja.errors import HttpError

from thorpat.rest_api.schemas.base_schemas import ErrorDetail, ErrorResponse


def http_exception_handler(request, exc: HttpError):
    return HttpResponse(
        ErrorResponse(  # type: ignore[call-arg]
            errors=[ErrorDetail(message=str(exc), code=str(exc.status_code))],
            success=False,
        ).model_dump_json(),
        status=200,
        content_type="application/json",
    )


def http_exception_handler_500(request, exc: Exception):
    return HttpResponse(
        ErrorResponse(  # type: ignore[call-arg]
            errors=[ErrorDetail(message=str(exc), code="500")],
            success=False,
        ).model_dump_json(),
        status=500,
        content_type="application/json",
    )
