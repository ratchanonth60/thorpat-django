from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from thorpat.apps.order.models import Order

User = get_user_model()


class AdminCustomerListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "dashboard/customer/list.html"
    context_object_name = "customers"
    paginate_by = 20

    def get_queryset(self):
        # แสดงเฉพาะ User ที่ไม่ใช่ staff/admin
        return User.objects.filter(is_staff=False).order_by("-date_joined")


class CustomerListView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = "dashboard/customer/list.html"
    context_object_name = "customers"
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(is_staff=False).order_by("-date_joined")


# เพิ่ม View ใหม่สำหรับหน้ารายละเอียดลูกค้า
class CustomerDetailView(LoginRequiredMixin, DetailView):
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
