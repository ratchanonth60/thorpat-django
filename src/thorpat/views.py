from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .apps.catalogue.models import Product


def home_view(request):
    # Fetch latest 8 products to display on the home page
    products = (
        Product.objects.filter(is_public=True)
        .prefetch_related("stockrecords")
        .order_by("-created_at")
    )

    return render(request, "home.html", {"products": products})


@login_required
def dashboard_view(request):
    # เปลี่ยน path ของ template ที่นี่
    return render(request, "dashboard/dashboard.html")


def error_404_view(request, exception):
    return render(request, "404.html", status=404)


def error_500_view(request):
    return render(request, "500.html", status=500)
