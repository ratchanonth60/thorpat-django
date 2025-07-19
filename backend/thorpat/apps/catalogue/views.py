from allauth.account.forms import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from thorpat.apps.cart.forms import AddToCartForm
from thorpat.apps.reviews.forms import ProductReviewForm
from thorpat.apps.reviews.models import ProductReview

from .filters import ProductFilter
from .models import Product


class ProductListView(ListView):
    model = Product
    template_name = "catalogue/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        # เพิ่ม .prefetch_related('stockrecords', 'images') เข้าไปใน queryset
        # เพื่อแก้ปัญหา ProgrammingError และ N+1 query problem
        queryset = (
            Product.objects.filter(is_public=True)
            .prefetch_related("stockrecords")
            .order_by("-created_at")
        )  # Apply filtering
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        context["cart_product_form"] = AddToCartForm()
        return context


class ProductListHTMXView(ProductListView):  # สามารถสืบทอดจาก ProductListView ได้เลย
    # template_name จะถูก override ใน get()

    def get(self, request, *args, **kwargs):
        # เรียก get_queryset และ get_context_data จาก parent class
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        # Render เฉพาะส่วนของ Grid และ Pagination
        html = render_to_string(
            "catalogue/partials/_product_grid.html",  # นี่คือ partial template ใหม่
            context,
            request=request,
        )
        return HttpResponse(html)


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalogue/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # ดึงรีวิวที่ได้รับการอนุมัติแล้ว
        context["reviews"] = product.reviews.filter(is_approved=True)
        context["review_count"] = context["reviews"].count()

        # เพิ่มฟอร์มรีวิวเข้าไปใน context ถ้า user login อยู่ และยังไม่เคยรีวิว
        if self.request.user.is_authenticated:
            if not ProductReview.objects.filter(
                product=product, user=self.request.user
            ).exists():
                context["review_form"] = ProductReviewForm()

        # คำนวณคะแนนเฉลี่ย
        if context["review_count"] > 0:
            total_rating = sum(review.rating for review in context["reviews"])
            context["average_rating"] = total_rating / context["review_count"]
        else:
            context["average_rating"] = 0

        return context
