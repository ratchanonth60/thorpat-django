from django.urls import path

from .views import AdminReportView

app_name = "reports"

urlpatterns = [
    path("", AdminReportView.as_view(), name="main"),
]
