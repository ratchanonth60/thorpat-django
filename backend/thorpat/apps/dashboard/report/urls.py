from django.urls import path

from .views import AdminReportView, SalesChartDataView

app_name = "reports"

urlpatterns = [
    path("", AdminReportView.as_view(), name="main"),
    path("sales-chart/", SalesChartDataView.as_view(), name="sales-chart"),
]
