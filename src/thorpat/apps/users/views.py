from allauth.account.forms import SetPasswordForm
from allauth.account.views import TemplateView
from django.contrib.auth import get_user_model  # Recommended way to get User model
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView

from thorpat.tasks.email import send_password_reset_email_task

from .forms import (
    CustomPasswordResetRequestForm,
)

User = get_user_model()


# +++++++++++++ ADD THE FOLLOWING VIEWS ++++++++++++++
class ValidateUsernameView(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get(
            "login", ""
        )  # 'login' is the field name from allauth form for username/email
        error_message = None

        if not username:
            error_message = "Username cannot be empty."
        elif len(username) < 3:
            error_message = "Username must be at least 3 characters."
        # Example: Check if username is taken (more relevant for registration)
        # For login, this specific check might not be ideal as it can confirm existence.
        # For this example, let's assume it's a generic validator.
        # elif User.objects.filter(username__iexact=username).exists() and request.resolver_match.url_name == 'validate_registration_username':
        #     error_message = f"Username '{username}' is already taken."

        if error_message:
            return HttpResponse(
                f'<p class="text-red-600 text-xs italic py-1">{error_message}</p>'
            )
        else:
            return HttpResponse(
                '<p class="text-green-600 text-xs italic py-1">✓ Valid format</p>'
            )  # Adjusted message


class MobileMenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "partials/mobile_menu.html")


class CustomPasswordResetView(FormView):
    template_name = "account/password_reset.html"  # เราจะสร้าง template นี้
    form_class = CustomPasswordResetRequestForm
    success_url = reverse_lazy("users:password_reset_done")
    token_generator = default_token_generator

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email__iexact=email)
            # เรียกใช้ Celery Task ที่คุณสร้างไว้
            send_password_reset_email_task.delay(user.pk)
        except User.DoesNotExist:
            pass
        return super().form_valid(form)


# View 2: หน้าแจ้งว่าส่งอีเมลแล้ว
class CustomPasswordResetDoneView(TemplateView):
    template_name = "account/password_reset_done.html"


class CustomPasswordResetConfirmView(FormView):
    template_name = "account/password_reset_confirm.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("users:password_reset_complete")


class CustomPasswordResetCompleteView(TemplateView):
    template_name = "account/password_reset_complete.html"
