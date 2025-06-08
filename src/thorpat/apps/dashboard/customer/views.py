from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

User = get_user_model()


class AdminCustomerListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "dashboard/customer/list.html"
    context_object_name = "customers"
    paginate_by = 20

    def get_queryset(self):
        # แสดงเฉพาะ User ที่ไม่ใช่ staff/admin
        return User.objects.filter(is_staff=False).order_by("-date_joined")
