from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View  # Base class for HTMX views
from django.views.generic import TemplateView  # Base class for TemplateView

from thorpat.apps.cart.utils import get_or_create_cart
from thorpat.apps.order.utils import OrderCreator, OrderPlacementError
from thorpat.apps.profiles.models import Address

from .forms import ShippingAddressForm


# Main View สำหรับแสดงหน้า Shipping Address (GET request)
class CheckoutShippingAddressView(LoginRequiredMixin, View):
    template_name = "checkout/shipping_address.html"

    def get(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        if cart.is_empty:
            messages.warning(request, _("Your cart is empty."))
            return redirect("cart:cart_detail")

        existing_addresses = Address.objects.filter(user=request.user)
        form = ShippingAddressForm()  # ฟอร์มสำหรับที่อยู่ใหม่

        context = {
            "addresses": existing_addresses,
            "form": form,
        }
        return render(request, self.template_name, context)


# HTMX View สำหรับการเลือกที่อยู่ที่มีอยู่แล้ว
class SelectShippingAddressHTMXView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        selected_address_id = request.POST.get(
            "selected_address"
        )  # ชื่อจาก radio button ใน address_summary.html

        if not selected_address_id:
            messages.error(request, _("Please select an address."))
            # ถ้าไม่เลือกอะไรมา ควรจะ re-render ส่วน addresses หรือแค่แสดง error
            # ในที่นี้ เราจะส่ง 400 เพื่อให้ HTMX ไม่ทำ redirect
            response = HttpResponse(_("Please select an address."), status=400)
            response["HX-Refresh"] = "true"  # Force browser refresh to show message
            return response

        try:
            address = Address.objects.get(id=selected_address_id, user=request.user)
            request.session["checkout_shipping_address_id"] = address.id
            messages.success(request, _("Shipping address selected."))

            # ส่ง HTMX-Redirect header เพื่อไปยังขั้นตอนต่อไป
            response = HttpResponse()
            response["HX-Redirect"] = reverse_lazy("checkout:payment_method")
            return response

        except Address.DoesNotExist:
            messages.error(request, _("Invalid address selected."))
            response = HttpResponse(_("Invalid address selected."), status=400)
            response["HX-Refresh"] = "true"
            return response


# HTMX View สำหรับการเพิ่มที่อยู่ใหม่
class AddShippingAddressHTMXView(LoginRequiredMixin, View):
    template_name_form_only = (
        "checkout/partials/_new_address_form.html"  # Partial template สำหรับฟอร์ม
    )

    def post(self, request, *args, **kwargs):
        form = ShippingAddressForm(request.POST)

        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()

            request.session["checkout_shipping_address_id"] = new_address.id
            messages.success(request, _("New address saved and selected."))

            # ส่ง HTMX-Redirect header เพื่อไปยังขั้นตอนต่อไป
            response = HttpResponse()
            response["HX-Redirect"] = reverse_lazy("checkout:payment_method")
            return response
        else:
            # ถ้าฟอร์มไม่ถูกต้อง ให้ render เฉพาะฟอร์มกลับไปพร้อม error
            # HTMX จะทำการ swap content ของเป้าหมายด้วย HTML ที่ส่งกลับมา
            context = {
                "form": form,
            }
            return render(
                request, self.template_name_form_only, context, status=400
            )  # ส่ง status 400 ด้วย


# View สำหรับหน้าวิธีการชำระเงิน
class CheckoutPaymentMethodView(LoginRequiredMixin, View):
    """
    Handles the display of payment methods and the final order placement.
    """

    def get(self, request, *args, **kwargs):
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


# View สำหรับหน้ายืนยันคำสั่งซื้อ
class OrderConfirmationView(TemplateView):
    """
    Displays a thank-you page after a successful order.
    """

    template_name = "checkout/thank_you.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_number"] = kwargs.get("order_number")
        return context
