from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    if isinstance(exc, APIException):
        return Response(
            {
                "code": exc.status_code,
                "message": exc.default_code,
                "detail": exc.detail,
            },
            status=status.HTTP_200_OK,
        )

    return exception_handler(exc, context)
