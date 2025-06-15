from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from thorpat.apps.catalogue.forms import ProductCategoryForm
from thorpat.apps.catalogue.models import ProductCategory


class AdminCategoryListView(LoginRequiredMixin, ListView):
    model = ProductCategory
    template_name = "dashboard/category/list.html"
    context_object_name = "categories"
    paginate_by = 10

    def get_queryset(self):
        return ProductCategory.objects.filter(user=self.request.user).order_by("name")


class AdminCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = "dashboard/category/form.html"
    success_url = reverse_lazy("dashboard:categories:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add New Category"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully.")
        form.instance.user = (
            self.request.user
        )  # Set the user to the current logged-in user
        return super().form_valid(form)


class AdminCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = "dashboard/category/form.html"
    success_url = reverse_lazy("dashboard:categories:list")

    def get_object(self):
        return get_object_or_404(
            ProductCategory, pk=self.kwargs.get("pk"), user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Edit Category: {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully.")
        return super().form_valid(form)


class AdminCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductCategory
    template_name = "dashboard/category/confirm_delete.html"
    success_url = reverse_lazy("dashboard:categories:list")

    def get_object(self):
        return get_object_or_404(
            ProductCategory, pk=self.kwargs.get("pk"), user=self.request.user
        )

    def post(self, request, *args, **kwargs):
        messages.success(
            request, f"Category '{self.get_object().name}' has been deleted."
        )
        return super().post(request, *args, **kwargs)
