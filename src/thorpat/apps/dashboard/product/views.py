from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, View

from thorpat.apps.catalogue.filters import ProductFilter
from thorpat.apps.catalogue.forms import ProductForm, StockRecordForm
from thorpat.apps.catalogue.models import Product


class AdminProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "dashboard/product/list.html"
    context_object_name = "products"
    paginate_by = 10

    def get_template_names(self):
        if self.request.htmx:
            return ["dashboard/product/_list_content.html"]
        return [self.template_name]

    def get_queryset(self):
        # --- เริ่มต้น Query ด้วยการกรองเฉพาะ user ปัจจุบัน ---
        queryset = super().get_queryset().filter(user=self.request.user)

        # ส่วน Filter เดิมยังคงทำงานได้ตามปกติ
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.prefetch_related("stockrecords").order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context

    def get_paginate_by(self, queryset):
        return self.request.GET.get("paginate_by", self.paginate_by)


class AdminProductCreateView(LoginRequiredMixin, View):
    template_name = "dashboard/product/form.html"

    def get(self, request, *args, **kwargs):
        product_form = ProductForm(user=request.user)  # ส่ง user ปัจจุบันไปยังฟอร์ม
        stock_form = StockRecordForm()
        context = {
            "product_form": product_form,
            "stock_form": stock_form,
            "page_title": "Add New Product",
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        product_form = ProductForm(request.POST, request.FILES)
        stock_form = StockRecordForm(request.POST)

        if product_form.is_valid() and stock_form.is_valid():
            product = product_form.save(commit=False)  # สามารถ save() ตรงๆ ได้เลย
            product.user = self.request.user
            product.save()
            # +++ เพิ่มบรรทัดนี้เข้ามาเพื่อบันทึก Categories (m2m) +++
            product_form.save(commit=False)
            product_form.save_m2m()

            stock_record = stock_form.save(commit=False)
            stock_record.product = product
            stock_record.save()

            messages.success(
                request, f"Product '{product.title}' has been created successfully."
            )
            return redirect("dashboard:products:list")

        # หากฟอร์มไม่ผ่านการตรวจสอบ ให้ส่งฟอร์มพร้อม error กลับไป
        context = {
            "product_form": product_form,
            "stock_form": stock_form,
            "page_title": "Add New Product",
        }
        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, context)


class AdminProductUpdateView(LoginRequiredMixin, View):
    template_name = "dashboard/product/form.html"

    def get_object(self):
        return get_object_or_404(
            Product, pk=self.kwargs.get("pk"), user=self.request.user
        )

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs.get("pk"))
        stockrecord = product.stockrecords.first()

        product_form = ProductForm(instance=product)
        stock_form = StockRecordForm(instance=stockrecord)

        context = {
            "product_form": product_form,
            "stock_form": stock_form,
            "page_title": f"Edit Product: {product.title}",
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs.get("pk"))
        stockrecord = product.stockrecords.first()

        product_form = ProductForm(request.POST, request.FILES, instance=product)
        stock_form = StockRecordForm(request.POST, instance=stockrecord)

        if product_form.is_valid() and stock_form.is_valid():
            product_form.save()
            stock_form.save()

            messages.success(
                request, f"Product '{product.title}' has been updated successfully."
            )
            return redirect("dashboard:products:list")

        context = {
            "product_form": product_form,
            "stock_form": stock_form,
            "page_title": f"Edit Product: {product.title}",
        }
        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, context)


class AdminProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "dashboard/product/confirm_delete.html"  # เราจะสร้าง template นี้ต่อไป
    success_url = reverse_lazy("dashboard:products:list")
    context_object_name = "product"

    def get_queryset(self):
        # --- บังคับให้ Query ได้เฉพาะ object ของ user ปัจจุบันเท่านั้น ---
        # ถ้า user พยายามเข้า URL ของ product คนอื่น จะเจอ 404 Not Found
        return self.model.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        messages.success(
            request, f"Product '{self.get_object().title}' has been deleted."
        )
        return super().post(request, *args, **kwargs)
