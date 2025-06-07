from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from thorpat.apps.cart.utils import get_or_create_cart
from thorpat.apps.order.utils import OrderCreator, OrderPlacementError
from thorpat.apps.profiles.models import Address

from .forms import ShippingAddressForm


class CheckoutShippingAddressView(LoginRequiredMixin, View):
    template_name = "checkout/shipping_address.html"

    def get(self, request, *args, **kwargs):
        # Get user's existing addresses
        existing_addresses = Address.objects.filter(user=request.user)

        # Get the current cart to check if it's empty
        cart = get_or_create_cart(request)
        if cart.is_empty:
            messages.warning(request, _("Your cart is empty."))
            return redirect("cart:cart_detail")

        # Form for entering a new address
        form = ShippingAddressForm()

        context = {
            "addresses": existing_addresses,
            "form": form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        if cart.is_empty:
            return redirect("cart:cart_detail")

        # Case 1: User selected an existing address
        selected_address_id = request.POST.get("selected_address")
        if selected_address_id:
            try:
                address = Address.objects.get(id=selected_address_id, user=request.user)
                # Store the chosen address ID in the session to use in the next steps
                request.session["checkout_shipping_address_id"] = address.id
                # Redirect to the next step (e.g., shipping method or payment)
                # For now, we'll create a placeholder URL 'checkout:payment'
                return redirect("checkout:payment_method")
            except Address.DoesNotExist:
                messages.error(request, _("Invalid address selected."))
                return redirect("checkout:shipping_address")

        # Case 2: User submitted the form for a new address
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            # Create a new address but don't save to DB yet
            new_address = form.save(commit=False)
            new_address.user = request.user  # Assign the current user
            new_address.save()

            # Store the new address ID in the session
            request.session["checkout_shipping_address_id"] = new_address.id
            messages.success(request, _("New address has been saved."))
            return redirect("checkout:payment_method")  # Redirect to next step

        # If form is invalid, re-render the page with errors
        existing_addresses = Address.objects.filter(user=request.user)
        context = {"addresses": existing_addresses, "form": form}
        return render(request, self.template_name, context)


class CheckoutPaymentMethodView(LoginRequiredMixin, View):
    """
    Placeholder view for the next step in checkout.
    """

    def get(self, request, *args, **kwargs):
        # A real implementation would show payment options (Credit Card, COD, etc.)
        # and would lead to the order confirmation page.

        # For now, this is just a placeholder to show the flow.

        # Retrieve the selected address from session to confirm it's being passed
        shipping_address_id = request.session.get("checkout_shipping_address_id")
        if not shipping_address_id:
            messages.error(request, _("Please select a shipping address first."))
            return redirect("checkout:shipping_address")

        address = Address.objects.get(id=shipping_address_id)
        cart = get_or_create_cart(request)

        # Here you would typically process payment and create the order.
        # We will build this "Order Placement" logic in the next step.

        return render(
            request, "checkout/payment_method.html", {"address": address, "cart": cart}
        )


class CheckoutPaymentMethodView(LoginRequiredMixin, View):
    """
    Handles the display of payment methods and the final order placement.
    """

    def get(self, request, *args, **kwargs):
        # ... (GET method remains the same) ...
        shipping_address_id = request.session.get("checkout_shipping_address_id")
        if not shipping_address_id:
            messages.error(request, _("Please select a shipping address first."))
            return redirect("checkout:shipping_address")

        address = Address.objects.get(id=shipping_address_id)
        cart = get_or_create_cart(request)

        # In a real scenario, you would pass payment forms/options here.
        return render(
            request, "checkout/payment_method.html", {"address": address, "cart": cart}
        )

    def post(self, request, *args, **kwargs):
        """
        This is where the order is actually placed.
        """
        # Retrieve all necessary info
        cart = get_or_create_cart(request)
        shipping_address_id = request.session.get("checkout_shipping_address_id")

        if not shipping_address_id or cart.is_empty:
            messages.error(
                request, _("An error occurred. Please start checkout again.")
            )
            return redirect("cart:cart_detail")

        shipping_address = get_object_or_404(
            Address, id=shipping_address_id, user=request.user
        )

        # Placeholder for payment processing logic
        # In a real app, you would process payment here with a gateway.
        # If payment fails, you would return an error.
        # For now, we assume payment is successful.

        # Use the OrderCreator to place the order
        creator = OrderCreator()
        try:
            order = creator.place_order(
                cart=cart,
                user=request.user,
                shipping_address=shipping_address,
                # billing_address can be different if you have a separate form for it
            )
        except OrderPlacementError as e:
            messages.error(request, str(e))
            return redirect("cart:cart_detail")

        # Order placed successfully.
        # Clear the checkout session data.
        del request.session["cart_id"]
        del request.session["checkout_shipping_address_id"]

        # Redirect to a thank-you page with the order number.
        return redirect("checkout:thank_you", order_number=order.number)


class OrderConfirmationView(TemplateView):
    """
    Displays a thank-you page after a successful order.
    """

    template_name = "checkout/thank_you.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_number"] = kwargs.get("order_number")
        return context
