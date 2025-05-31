from rest_framework.response import Response
from rest_framework import status


class ResponseAPI(Response):
    def __init__(
        self, data=None, status=status.HTTP_200_OK, message=None, errors=None, **kwargs
    ):
        response_data = {
            "success": status < 300,
            "message": message if message else "Success" if status < 300 else "Failure",
            "data": data,
            "errors": errors,
        }
        super().__init__(response_data, status=status, **kwargs)
