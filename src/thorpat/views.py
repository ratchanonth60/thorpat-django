from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home_view(request):
    return render(request, "home.html")


@login_required
def dashboard_view(request):
    # เปลี่ยน path ของ template ที่นี่
    return render(request, "dashboard/dashboard.html")
