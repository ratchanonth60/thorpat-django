from thorpat.apps.cart.utils import get_or_create_cart


class CartMiddleware:
    """
    Middleware to attach the cart object to the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach the cart to the request object so it's available in templates
        request.cart = get_or_create_cart(request)
        response = self.get_response(request)
        return response
