from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views import View

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


class SetCurrencyView(View):
    """
    View to set the currency in the session.
    """

    def post(self, request, *args, **kwargs):
        # รับค่า currency จากฟอร์ม
        currency_code = request.POST.get("currency", settings.THORPAT_DEFAULT_CURRENCY)

        # ตรวจสอบว่า currency ที่เลือกมีอยู่ในรายการที่อนุญาตหรือไม่
        available_codes = [code for code, name in settings.THORPAT_AVAILABLE_CURRENCIES]
        if currency_code in available_codes:
            request.session["currency"] = currency_code

        # กลับไปยังหน้าเดิมที่ผู้ใช้อยู่
        return redirect(request.META.get("HTTP_REFERER", "/"))
