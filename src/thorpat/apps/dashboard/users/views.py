import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, UpdateView

from thorpat.apps.activitylog.models import ActivityLog
from thorpat.apps.users.forms import UserProfileUpdateForm

User = get_user_model()


class UserInfoView(LoginRequiredMixin, TemplateView):
    """
    View for displaying user information on their dashboard.
    This was previously named UserDashboardView in our examples.
    """

    template_name = (
        "dashboard/user/info.html"  # Path to your user info/dashboard template
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_user"] = self.request.user
        # Add any other context data needed for the info page
        # context['profile'] = self.request.user.profile # If you have a related profile model
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
