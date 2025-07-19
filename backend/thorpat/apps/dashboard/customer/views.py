from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from thorpat.apps.dashboard.customer.forms import CustomerForm
from thorpat.apps.order.models import Order

User = get_user_model()


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff  # type: ignore[return-value]


class CustomerListView(
    StaffRequiredMixin, ListView
):  # เปลี่ยน LoginRequiredMixin เป็น StaffRequiredMixin
    model = User
    template_name = "dashboard/customer/list.html"
    context_object_name = "customers"
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(is_staff=False).order_by("-date_joined")


class CustomerDetailView(
    StaffRequiredMixin, DetailView
):  # เปลี่ยน LoginRequiredMixin เป็น StaffRequiredMixin
    model = get_user_model()
    template_name = "dashboard/customer/detail.html"
    context_object_name = "customer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        context["orders"] = Order.objects.filter(user=customer).order_by(
            "-date_placed"
        )[:10]
        context["total_orders"] = Order.objects.filter(user=customer).count()
        context["total_spent"] = sum(
            order.total_incl_tax for order in Order.objects.filter(user=customer)
        )
        return context


# เพิ่มส่วนนี้
class CustomerCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = CustomerForm
    template_name = "dashboard/customer/form.html"
    success_url = reverse_lazy("dashboard:customer-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Add New Customer")
        return context

    def form_valid(self, form):
        # ตรวจสอบให้แน่ใจว่าผู้ใช้ที่สร้างใหม่ไม่ใช่ is_staff และ is_superuser
        form.instance.is_staff = False
        form.instance.is_superuser = False
        response = super().form_valid(form)
        messages.success(
            self.request,
            _("Customer '%(username)s' created successfully!")
            % {"username": self.object.username},
        )
        return response


class CustomerUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = CustomerForm
    template_name = "dashboard/customer/form.html"
    context_object_name = "customer"
    success_url = reverse_lazy("dashboard:customer-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Customer")
        context["page_title"] = f"Edit Customer: {self.object.username}"
        return context

    def form_valid(self, form):
        # ป้องกันการเปลี่ยน is_staff/is_superuser ผ่านหน้านี้
        if form.instance.is_staff and not self.request.user.is_superuser:
            # ถ้าผู้ใช้ที่กำลังแก้ไขเป็น staff และผู้แก้ไขไม่ใช่ superuser
            # อาจจะต้องเพิ่มการจัดการข้อผิดพลาดหรือป้องกันไม่ให้แก้ไข is_staff
            pass  # หรือ form.add_error(...)

        response = super().form_valid(form)
        messages.success(
            self.request,
            _("Customer '%(username)s' updated successfully!")
            % {"username": self.object.username},
        )
        return response


class CustomerDeleteView(StaffRequiredMixin, DeleteView):
    model = User
    template_name = "dashboard/customer/confirm_delete.html"
    context_object_name = "customer"
    success_url = reverse_lazy("dashboard:customer-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Delete Customer")
        return context

    def form_valid(self, form):
        # ตรวจสอบว่ากำลังลบผู้ใช้ที่เป็น staff/superuser หรือไม่
        if self.object.is_staff or self.object.is_superuser:
            messages.error(
                self.request,
                _("Cannot delete staff or superuser accounts through this interface."),
            )
            return self.form_invalid(form)  # ป้องกันการลบ
        response = super().form_valid(form)
        messages.success(
            self.request,
            _("Customer '%(username)s' deleted successfully!")
            % {"username": self.object.username},
        )
        return response
