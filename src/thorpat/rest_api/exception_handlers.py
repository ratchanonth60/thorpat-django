import json
from django.http import Http404, HttpResponse
from ninja.errors import AuthenticationError, HttpError, ValidationError

from thorpat.rest_api.schemas.base_schemas import ErrorDetail, ErrorResponse


def http_exception_handler_auth(request, exc: AuthenticationError):
    return HttpResponse(
        ErrorResponse(  # type: ignore[call-arg]
            errors=[ErrorDetail(message=str(exc), code=str(exc.status_code))],
            success=False,
        ).model_dump_json(),
        status=200,
        content_type="application/json",
    )


def http_exception_handler_404(request, exc: Http404):
    return HttpResponse(
        ErrorResponse(  # type: ignore[call-arg]
            errors=[ErrorDetail(message=str(exc), code="404")],
            success=False,
        ).model_dump_json(),
        status=200,
        content_type="application/json",
    )


def http_exception_handler_422(request, exc: ValidationError):
    """
    Handles ninja.errors.ValidationError (typically for Pydantic validation errors).
    Returns a 200 OK response with success=False and detailed error messages.
    """
    error_details = []
    for error_item in exc.errors:  # exc.errors is a list of dicts from Pydantic
        # field_name = None
        # error_item['loc'] is a tuple, e.g., ('body', 'field_name') or ('query', 'param_name')
        # We usually want the last part as the field identifier.
        # loc = error_item.get("loc")
        # if loc and len(loc) > 0:
        #     field_name = str(loc[-1])  # Get the actual field name

        error_details.append(
            ErrorDetail(
                message=error_item.get(
                    "type", "validation_error"
                ),  # Use Pydantic's error type as code,
                field=error_item.get("msg", "Invalid input."),
                code="422",
            )
        )
    return HttpResponse(
        ErrorResponse(
            message="Validation failed. Please check your input.",  # General message for the 422 error
            errors=error_details,
            success=False,
        ).model_dump_json(),
        status=200,  # Consistent with other custom handlers in this project
        content_type="application/json",
    )


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
        status=200,
        content_type="application/json",
    )
