from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from thorpat.apps.catalogue.models import Product

from .forms import ProductReviewForm
from .models import ProductReview


class AddProductReviewView(LoginRequiredMixin, CreateView):
    model = ProductReview
    form_class = ProductReviewForm
    template_name = "reviews/add_review.html"  # เราจะสร้าง template นี้ในขั้นตอนต่อไป

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, slug=self.kwargs["slug"])
        # ตรวจสอบว่า user เคยรีวิวสินค้านี้ไปแล้วหรือยัง
        if ProductReview.objects.filter(
            product=self.product, user=request.user
        ).exists():
            messages.warning(request, _("You have already reviewed this product."))
            return redirect(self.product.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = self.product
        messages.success(self.request, _("Thank you! Your review has been submitted."))
        return super().form_valid(form)

    def get_success_url(self):
        return self.product.get_absolute_url()
