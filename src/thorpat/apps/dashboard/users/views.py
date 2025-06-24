import json
from datetime import datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, TemplateView, UpdateView

from thorpat.apps.activitylog.models import ActivityLog
from thorpat.apps.catalogue.models import Product, ProductCategory
from thorpat.apps.order.models import Order, OrderLine
from thorpat.apps.users.forms import UserProfileUpdateForm
from thorpat.apps.users.models import User


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class DashboardUserView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/user/info.html"

    def calculate_sales_data(self, queryset, period):
        """
        ฟังก์ชันใหม่สำหรับคำนวณและจัดกลุ่มข้อมูลยอดขายตามช่วงเวลาที่เลือก
        - ถ้าเป็นรายวัน (7, 30 วัน) จะจัดกลุ่มข้อมูลเป็นรายวัน
        - ถ้าเป็นรายปีหรือทั้งหมด จะจัดกลุ่มข้อมูลเป็นรายเดือน
        """
        if period in ["last_7_days", "last_30_days"]:
            # จัดกลุ่มข้อมูลเป็นรายวัน
            sales = (
                queryset.annotate(day=TruncDay("date_placed"))
                .values("day")
                .annotate(total=Sum("total_excl_tax"))
                .order_by("day")
            )
            labels = [s["day"].strftime("%b %d") for s in sales]
            data = [float(s["total"]) for s in sales]
            return {"labels": labels, "data": data}
        else:  # this_year, all_time
            # จัดกลุ่มข้อมูลเป็นรายเดือน
            sales = (
                queryset.annotate(month=TruncMonth("date_placed"))
                .values("month")
                .annotate(total=Sum("total_excl_tax"))
                .order_by("month")
            )
            labels = [s["month"].strftime("%B %Y") for s in sales]
            data = [float(s["total"]) for s in sales]
            return {"labels": labels, "data": data}

    def get_monthly_sales_data(self):
        # Generate a list of months for the last year
        today = timezone.now()
        months = [(today - timedelta(days=30 * i)).strftime("%B") for i in range(12)]
        months.reverse()

        sales_data = {month: 0 for month in months}

        # TEMPORARY FIX: Removed date filtering to fetch all orders
        # last_12_months = today - timedelta(days=365)
        orders = (
            # Order.objects.filter(date_placed__gte=last_12_months)
            Order.objects.all()  # ดึงข้อมูล Order ทั้งหมดโดยไม่กรองวันที่
            .values("date_placed__month", "date_placed__year")
            .annotate(total_sales=Sum("total_excl_tax"))
            .order_by("date_placed__year", "date_placed__month")
        )

        # Since we removed the date filter, let's adjust how we populate sales_data
        # This part will now just aggregate data by month/year regardless of the last 12 months
        processed_sales_data = {}
        for order in orders:
            # Create a key like "June 2025"
            month_year_key = datetime(
                year=order["date_placed__year"],
                month=order["date_placed__month"],
                day=1,
            ).strftime("%B %Y")

            if month_year_key not in processed_sales_data:
                processed_sales_data[month_year_key] = 0
            processed_sales_data[month_year_key] += float(order["total_sales"])

        # If there's no data, return empty lists
        if not processed_sales_data:
            return {"labels": [], "data": []}

        return {
            "labels": list(processed_sales_data.keys()),
            "data": list(processed_sales_data.values()),
        }

    def get_order_status_data(self):
        status_counts = (
            Order.objects.values("status")
            .annotate(count=Count("status"))
            .order_by("status")
        )
        labels = [
            dict(Order.STATUS_CHOICES).get(item["status"], item["status"])
            for item in status_counts
        ]
        data = [item["count"] for item in status_counts]
        return {"labels": labels, "data": data}

    def get_top_selling_products(self, limit=5):
        return (
            OrderLine.objects.values("product__title")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")[:limit]
        )

    def get_product_by_category_data(self):
        """
        ฟังก์ชันใหม่สำหรับดึงข้อมูลจำนวนสินค้าในแต่ละ Category
        """
        category_data = (
            ProductCategory.objects.annotate(num_products=Count("products"))
            .filter(num_products__gt=0)
            .order_by("-num_products")
        )
        labels = [category.name for category in category_data]
        data = [category.num_products for category in category_data]
        return {"labels": labels, "data": data}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. รับค่า 'period' จาก request, ถ้าไม่มีให้ใช้ 'this_year' เป็นค่าเริ่มต้น
        period = self.request.GET.get("period", "this_year")

        # 2. สร้าง Queryset เริ่มต้นและกรองข้อมูลตาม 'period'
        orders_qs = Order.objects.all()
        today = timezone.now()

        if period == "last_7_days":
            start_date = today - timedelta(days=7)
            orders_qs = orders_qs.filter(date_placed__gte=start_date)
        elif period == "last_30_days":
            start_date = today - timedelta(days=30)
            orders_qs = orders_qs.filter(date_placed__gte=start_date)
        elif period == "this_year":
            orders_qs = orders_qs.filter(date_placed__year=today.year)
        # ถ้าเป็น 'all_time' ก็ไม่ต้องกรอง

        # Context สำหรับการ์ดสรุปและตาราง (คำนวณจากข้อมูลทั้งหมด)
        context["total_sales"] = (
            Order.objects.aggregate(Sum("total_excl_tax"))["total_excl_tax__sum"] or 0
        )
        context["total_customers"] = User.objects.filter(is_staff=False).count()
        context["total_orders"] = Order.objects.count()
        context["total_products"] = Product.objects.count()
        context["recent_activities"] = ActivityLog.objects.all().order_by("-timestamp")[
            :10
        ]
        context["top_selling_products"] = (
            OrderLine.objects.values("product__title")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")[:5]
        )

        # Context สำหรับกราฟ (คำนวณจากข้อมูลที่กรองแล้ว)
        context["monthly_sales"] = self.calculate_sales_data(orders_qs, period)
        context["order_status_data"] = {
            "labels": [
                dict(Order.STATUS_CHOICES).get(item["status"], item["status"])
                for item in Order.objects.values("status")
                .annotate(count=Count("status"))
                .order_by("status")
                if item["status"]
            ],
            "data": [
                item["count"]
                for item in Order.objects.values("status")
                .annotate(count=Count("status"))
                .order_by("status")
                if item["status"]
            ],
        }
        context["product_by_category_data"] = {
            "labels": [
                c.name
                for c in ProductCategory.objects.annotate(n=Count("products")).filter(
                    n__gt=0
                )
            ],
            "data": [
                c.n
                for c in ProductCategory.objects.annotate(n=Count("products")).filter(
                    n__gt=0
                )
            ],
        }

        # ส่งค่า period กลับไปให้ template เพื่อให้ dropdown แสดงค่าที่เลือกไว้ถูกต้อง
        context["period"] = period

        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileUpdateForm  # ตรวจสอบว่า Form นี้ถูกสร้างและ import ถูกต้อง
    template_name = "dashboard/user/update.html"  # Template หลักที่ include partial
    # success_url ไม่จำเป็นต้องใช้ถ้า HTMX จัดการ response

    def get_object(self, queryset=None):
        return self.request.user

    def get_template_names(self):
        if self.request.htmx:
            return ["dashboard/user/partials/update_form_partial.html"]
        return [self.template_name]

    def form_valid(self, form):
        self.object = form.save()
        # messages.success(self.request, 'Your profile has been updated successfully!') # Django messages อาจจะไม่แสดงทันทีกับ HTMX swap

        if self.request.htmx:
            # ส่ง partial กลับไป พร้อมกับ trigger event ให้ client side (HTMX) จัดการ
            response = HttpResponse(
                render_to_string(
                    self.get_template_names()[0],
                    {"form": form, "success_message": "Profile updated successfully!"},
                )
            )
            response["HX-Trigger"] = json.dumps(
                {
                    "showMessage": {
                        "message": "Profile updated successfully!",
                        "level": "success",
                    },
                    "profileUpdated": {},  # Event อื่นๆ ที่ client อาจจะ listen
                }
            )
            return response
        return super().form_valid(
            form
        )  # Fallback สำหรับ non-HTMX request (จะทำ redirect)

    def form_invalid(self, form):
        if self.request.htmx:
            # ส่ง partial ที่มี error กลับไป
            # ตั้ง status code เป็น 422 (Unprocessable Entity) เพื่อให้ HTMX ทราบว่ามี error แต่ยัง render response body
            return render(
                self.request, self.get_template_names()[0], {"form": form}, status=422
            )
        return super().form_invalid(form)

    def get_success_url(self):
        # This is called for non-HTMX successful submissions.
        # For HTMX, we handle the response in form_valid.
        return reverse_lazy("dashboard:user_info")  # หรือ URL ที่เหมาะสม


class UserRecentActivityView(LoginRequiredMixin, ListView):
    model = ActivityLog  # ระบุ Model ที่จะใช้ (ถ้าคุณมี ActivityLog model)
    template_name = "dashboard/user/partials/recent_activity_list.html"  # Template สำหรับ HTML fragment
    context_object_name = "activities"
    paginate_by = 5  # แสดง 5 รายการต่อหน้า (ถ้าต้องการ pagination)

    def get_queryset(self):
        # ดึงเฉพาะ activity ของผู้ใช้ที่ login อยู่
        return ActivityLog.objects.filter(user=self.request.user).order_by(
            "-timestamp"
        )[: self.paginate_by]  # เอา 5 รายการล่าสุด

    def get_template_names(self):
        # ถ้า request มาจาก HTMX ให้ใช้ partial template
        # (อาจจะไม่จำเป็นถ้า ListView render partial โดยตรงอยู่แล้ว หรือถ้าคุณไม่ต้องการสลับ template)
        if self.request.htmx:
            return [self.template_name]
        # ถ้าไม่ใช่ HTMX request (เช่น เข้า URL นี้ตรงๆ) อาจจะ render ใน context ของหน้าอื่น หรือ redirect
        # หรือจะใช้ template เดิมก็ได้ ขึ้นอยู่กับว่าต้องการให้ URL นี้เข้าถึงโดยตรงได้หรือไม่
        return [self.template_name]  # หรือ template อื่นที่เหมาะสมถ้าไม่ใช่ HTMX


class SalesChartHTMXView(DashboardUserView):
    """
    View นี้จะถูกเรียกโดย HTMX เพื่อส่งเฉพาะ HTML ของกราฟ Sales
    """

    template_name = "dashboard/user/partials/charts/sales_over_time.html"


class OrderStatusChartHTMXView(DashboardUserView):
    """
    View นี้จะถูกเรียกโดย HTMX เพื่อส่งเฉพาะ HTML ของกราฟ Order Status
    """

    template_name = "dashboard/user/partials/charts/order_status.html"


class ProductCategoryChartHTMXView(DashboardUserView):
    """
    View นี้จะถูกเรียกโดย HTMX เพื่อส่งเฉพาะ HTML ของกราฟ Product Category
    """

    template_name = "dashboard/user/partials/charts/products_by_category.html"


class SummaryCardsHTMXView(DashboardUserView):
    """
    View นี้จะถูกเรียกโดย HTMX เพื่อส่งเฉพาะ HTML ของการ์ดข้อมูลสรุป
    """

    template_name = "dashboard/user/partials/summary_cards.html"
