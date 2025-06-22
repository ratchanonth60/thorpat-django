from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from thorpat.apps.catalogue.models import Product

from .forms import CartLineUpdateForm
from .models import CartLine
from .utils import get_or_create_cart


class CartDetailView(TemplateView):
    template_name = "cart/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request)

        # Create a form for each line in the cart
        line_forms = []
        for line in cart.lines.all():
            form = CartLineUpdateForm(initial={"quantity": line.quantity})
            line_forms.append({"line": line, "form": form})

        context["cart"] = cart
        context["line_forms"] = line_forms
        return context


class AddToCartView(View):
    def post(self, request, product_id):
        cart = get_or_create_cart(request)
        product = get_object_or_404(Product, id=product_id)

        quantity = int(request.POST.get("quantity", 1))

        if (
            not product.is_available_to_buy
            or product.primary_stockrecord.net_stock_level < quantity
        ):
            messages.error(
                request,
                _(
                    "Sorry, this product is out of stock or not enough quantity available."
                ),
            )
            # สำหรับ error, redirect กลับไปที่หน้าเดิม
            return redirect("catalogue:product_detail", slug=product.slug)

        line, created = cart.add_product(product, quantity)

        if created:
            messages.success(
                request,
                _("'%(product)s' has been added to your cart.")
                % {"product": product.title},
            )
        else:
            messages.success(
                request,
                _("Quantity for '%(product)s' has been updated in your cart.")
                % {"product": product.title},
            )

        # ถ้า request มาจาก HTMX ให้ render เฉพาะส่วนของ cart link กลับไป
        if request.htmx:
            # Context ที่ส่งกลับไปต้องมี `request.cart` ซึ่ง middleware จัดการให้แล้ว
            return render(request, "cart/partials/cart_link.html")

        # Fallback สำหรับกรณีที่ไม่ใช่ HTMX (ซึ่งไม่น่าจะเกิดขึ้นจาก form ปัจจุบัน)
        return redirect("cart:cart_detail")


class UpdateCartLineView(View):
    def post(self, request, line_id):
        line = get_object_or_404(CartLine, id=line_id)
        form = CartLineUpdateForm(request.POST)

        if form.is_valid():
            new_quantity = form.cleaned_data["quantity"]

            # Basic stock check
            if line.product.primary_stockrecord.net_stock_level < new_quantity:
                messages.error(
                    request,
                    _("Sorry, there is not enough stock for '%(product)s'.")
                    % {"product": line.product.title},
                )
            else:
                line.quantity = new_quantity
                line.save()
                messages.success(request, _("Your cart has been updated."))
        else:
            messages.error(request, _("Please enter a valid quantity."))

        if request.htmx:
            # Create a new form for the updated line
            form = CartLineUpdateForm(initial={"quantity": line.quantity})
            context = {
                "item": {"line": line, "form": form},
                "cart": get_or_create_cart(request),
            }
            return render(request, "cart/partials/cart_line.html", context)

        return redirect("cart:cart_detail")


class RemoveFromCartView(View):
    def post(self, request, line_id):
        line = get_object_or_404(CartLine, id=line_id)
        line.delete()
        messages.success(request, _("Item has been removed from your cart."))
        return redirect("cart:cart_detail")
