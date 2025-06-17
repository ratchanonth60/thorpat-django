from allauth.account.forms import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from thorpat.apps.cart.forms import AddToCartForm

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

    def get_queryset(self):
        # --- MODIFICATION START ---
        # แก้ไข Queryset ให้ดึงข้อมูล stockrecords และ images มาล่วงหน้า
        # เพื่อป้องกันข้อผิดพลาด ProgrammingError ตอนแสดงผล display_price
        # และช่วยเพิ่มประสิทธิภาพในการโหลดรูปภาพ
        return (
            super()
            .get_queryset()
            .filter(is_public=True)
            .prefetch_related("stockrecords")
        )
        # --- MODIFICATION END ---

    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), slug=self.kwargs["slug"])
