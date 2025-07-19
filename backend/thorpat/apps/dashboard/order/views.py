from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from thorpat.apps.order.models import Order


class OrderListView(LoginRequiredMixin, ListView):
    """
    View for listing a user's orders.
    """

    model = Order
    template_name = "dashboard/order/list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        # Users should only see their own orders, most recent first.
        return Order.objects.filter(user=self.request.user).order_by("-date_placed")


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    View for showing a single order's details.
    """

    model = Order
    template_name = "dashboard/order/detail.html"
    context_object_name = "order"

    def get_queryset(self):
        # Ensure users can only access their own orders.
        return Order.objects.filter(user=self.request.user)

