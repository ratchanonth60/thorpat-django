import json
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.views.generic import TemplateView

from thorpat.apps.order.models import Order


class AdminReportView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/report/main.html"


class SalesChartDataView(LoginRequiredMixin, TemplateView):
    """
    Provides data for the monthly sales chart, loaded via HTMX.
    This view now uses a Class-Based View structure for consistency.
    """

    template_name = "dashboard/report/partials/sales_chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate data for the last 6 months
        six_months_ago = timezone.now() - timedelta(days=180)

        sales_data = (
            Order.objects.filter(date_placed__gte=six_months_ago)
            .annotate(month=TruncMonth("date_placed"))
            .values("month")
            .annotate(total_sales=Sum("total_excl_tax"))
            .order_by("month")
        )

        # Format data for Chart.js
        labels = [sale["month"].strftime("%b %Y") for sale in sales_data]
        data = [float(sale["total_sales"]) for sale in sales_data]

        # If no data, provide some dummy data to show an empty chart
        if not labels:
            labels = [
                (timezone.now() - timedelta(days=30 * i)).strftime("%b %Y")
                for i in range(6)
            ][::-1]
            data = [0, 0, 0, 0, 0, 0]

        context["labels"] = json.dumps(labels)
        context["data"] = json.dumps(data)
        return context
