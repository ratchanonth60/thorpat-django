from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class AdminOrderListView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/management/order_list.html"


class AdminProductListView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/management/product_list.html"


class AdminCustomerListView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/management/customer_list.html"


class AdminReportView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/management/report_main.html"
