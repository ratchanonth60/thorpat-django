from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .apps.catalogue.models import Product


def home_view(request):
    # Fetch latest 8 products to display on the home page
    featured_products = Product.objects.filter(is_public=True).order_by("-created_at")[
        :8
    ]

    context = {"featured_products": featured_products}
    return render(request, "home.html", context)


@login_required
def dashboard_view(request):
    # เปลี่ยน path ของ template ที่นี่
    return render(request, "dashboard/dashboard.html")

