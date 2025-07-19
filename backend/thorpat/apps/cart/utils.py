from .models import Cart


def get_or_create_cart(request):
    """
    Retrieves the cart for the current user.
    - If user is authenticated, retrieves their latest open cart or creates one.
    - If user is anonymous, uses the session to store the cart ID.
    """
    cart = None
    if request.user.is_authenticated:
        # User is logged in. Try to get their latest open cart.
        cart, created = Cart.objects.get_or_create(
            owner=request.user, status=Cart.OPEN, defaults={}
        )
    else:
        # Anonymous user. Use the session.
        cart_id = request.session.get("cart_id")
        if cart_id:
            try:
                cart = Cart.objects.get(
                    id=cart_id, owner__isnull=True, status=Cart.OPEN
                )
            except Cart.DoesNotExist:
                # Cart ID in session is invalid (e.g., submitted or deleted).
                # Create a new cart.
                cart = Cart.objects.create()
                request.session["cart_id"] = cart.id
        else:
            # No cart ID in session, create a new cart.
            cart = Cart.objects.create()
            request.session["cart_id"] = cart.id
    return cart
