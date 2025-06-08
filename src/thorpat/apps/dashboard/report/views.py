from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class AdminReportView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/report/main.html"
