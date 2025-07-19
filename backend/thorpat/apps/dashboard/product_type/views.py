from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from thorpat.apps.catalogue.forms import ProductTypeForm
from thorpat.apps.catalogue.models import ProductType


class AdminProductTypeListView(LoginRequiredMixin, ListView):
    model = ProductType
    template_name = "dashboard/product_type/list.html"
    context_object_name = "product_types"
    paginate_by = 15
    ordering = ["name"]


class AdminProductTypeCreateView(LoginRequiredMixin, CreateView):
    model = ProductType
    form_class = ProductTypeForm
    template_name = "dashboard/product_type/form.html"
    success_url = reverse_lazy("dashboard:product_types:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add New Product Type"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"Product Type '{form.instance.name}' created successfully."
        )
        return super().form_valid(form)


class AdminProductTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductType
    form_class = ProductTypeForm
    template_name = "dashboard/product_type/form.html"
    success_url = reverse_lazy("dashboard:product_types:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Edit Product Type: {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"Product Type '{form.instance.name}' updated successfully."
        )
        return super().form_valid(form)


class AdminProductTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductType
    template_name = "dashboard/product_type/confirm_delete.html"
    success_url = reverse_lazy("dashboard:product_types:list")
    context_object_name = "product_type"

    def post(self, request, *args, **kwargs):
        messages.success(
            request, f"Product Type '{self.get_object().name}' has been deleted."
        )
        return super().post(request, *args, **kwargs)
