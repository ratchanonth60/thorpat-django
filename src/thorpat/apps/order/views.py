from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order


class OrderHistoryView(LoginRequiredMixin, ListView):
    """
    Display the order history for the currently logged-in user.
    """

    model = Order
    template_name = "order/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        # Return orders for the current user, ordered by most recent
        return Order.objects.filter(user=self.request.user).order_by("-date_placed")


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Display the details of a single order.
    """

    model = Order
    template_name = "order/order_detail.html"
    context_object_name = "order"
    # Use 'number' field for lookup instead of 'pk'
    slug_field = "number"
    slug_url_kwarg = "order_number"

    def get_queryset(self):
        # Ensure the user can only see their own orders
        return Order.objects.filter(user=self.request.user)
