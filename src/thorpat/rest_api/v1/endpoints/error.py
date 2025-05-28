from ninja import Router
from ninja.errors import HttpError

router = Router(tags=["error"])


@router.get("/error")
def some_operation(request):
    if True:
        raise HttpError(403, "Service Unavailable. Please retry later.")


@router.get("/exception")
def exception_handler(request):
    if True:
        raise Exception("An unexpected error occurred.")
