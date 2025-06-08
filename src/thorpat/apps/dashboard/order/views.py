from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from thorpat.apps.order.models import Order


class AdminOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "dashboard/order/list.html"  # ใช้ Template เดิมไปก่อน
    context_object_name = "orders"
    paginate_by = 15
    ordering = ["-date_placed"]
