from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from thorpat.apps.partner.forms import PartnerForm
from thorpat.apps.partner.models import Partner


class AdminPartnerListView(LoginRequiredMixin, ListView):
    model = Partner
    template_name = "dashboard/partner/list.html"
    context_object_name = "partners"
    paginate_by = 15
    ordering = ["name"]


class AdminPartnerCreateView(LoginRequiredMixin, CreateView):
    model = Partner
    form_class = PartnerForm
    template_name = "dashboard/partner/form.html"
    success_url = reverse_lazy("dashboard:partners:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add New Partner"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"Partner '{form.instance.name}' created successfully."
        )
        return super().form_valid(form)


class AdminPartnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Partner
    form_class = PartnerForm
    template_name = "dashboard/partner/form.html"
    success_url = reverse_lazy("dashboard:partners:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Edit Partner: {self.object.name}"
        return context

    def form_valid(self, form):
        messages.success(
            self.request, f"Partner '{form.instance.name}' updated successfully."
        )
        return super().form_valid(form)


class AdminPartnerDeleteView(LoginRequiredMixin, DeleteView):
    model = Partner
    template_name = "dashboard/partner/confirm_delete.html"
    success_url = reverse_lazy("dashboard:partners:list")
    context_object_name = "partner"

    def post(self, request, *args, **kwargs):
        messages.success(
            request, f"Partner '{self.get_object().name}' has been deleted."
        )
        return super().post(request, *args, **kwargs)
