import logging

from rest_framework import status as drf_http_status
from rest_framework.views import exception_handler as drf_exception_handler

from thorpat.api.v1.utils import ResponseAPI

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response_from_drf = drf_exception_handler(exc, context)
    print(f"Custom exception handler called with: {exc}, context: {context}")
    if response_from_drf is not None:
        drf_error_payload = response_from_drf.data
        actual_http_status_code = (
            response_from_drf.status_code
        )  # status code ที่แท้จริงจาก DRF
        custom_message = None

        if isinstance(drf_error_payload, dict):
            if "detail" in drf_error_payload and len(drf_error_payload) == 1:
                custom_message = str(drf_error_payload["detail"])
            elif actual_http_status_code == drf_http_status.HTTP_400_BAD_REQUEST:
                custom_message = "Validation failed. Please check submitted data."
        elif isinstance(drf_error_payload, list) and drf_error_payload:
            if isinstance(drf_error_payload[0], str):
                custom_message = drf_error_payload[0]
            else:
                custom_message = "Multiple errors occurred."
        elif isinstance(drf_error_payload, str):
            custom_message = drf_error_payload
            drf_error_payload = {"detail": drf_error_payload}

        return ResponseAPI(
            status=response_from_drf.status_code,
            data=None,
            errors=drf_error_payload,
            message=custom_message,  # ResponseAPI จะใช้ "Failure" ถ้า custom_message เป็น None และ logical_status เป็น error
            code=response_from_drf.status_code,
        )

    logger.error(
        f"Unhandled exception in custom_exception_handler: {exc}", exc_info=True
    )
    print(f"Unhandled exception in custom_exception_handler: {exc}, context: {context}")
    return ResponseAPI(
        status=drf_http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        data=None,
        errors={
            "detail": "An unexpected server error occurred. Please try again later."
        },
        message="Internal Server Error",
        code=drf_http_status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
