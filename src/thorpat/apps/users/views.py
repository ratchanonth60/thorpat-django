from allauth.account.forms import LoginForm, SetPasswordForm
from allauth.account.views import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _  # Import gettext for translation
from django.views import View  # Base class for simple CBVs
from django.views.generic import DetailView, RedirectView, UpdateView
from django.views.generic.edit import FormView

from thorpat.tasks.email import send_password_reset_email_task

from .forms import (
    CustomPasswordResetRequestForm,
    UserProfileUpdateForm,
)

User = get_user_model()


# HTMX Validation CBV for the 'login' field (username/email) in login.html
class ValidateLoginFieldView(View):
    def post(self, request, *args, **kwargs):
        login_value = request.POST.get("login", "").strip()
        error_message = ""

        if not login_value:
            error_message = _("This field cannot be empty.")
        elif "@" in login_value:
            try:
                django_validate_email(login_value)
            except ValidationError:
                error_message = _("Please enter a valid email address.")
        elif len(login_value) < 3:  # Basic length check for username
            error_message = _("Username must be at least 3 characters.")

        # Note: For login, we avoid checking if the user exists for security reasons
        # (e.g., to prevent user enumeration attacks).

        if error_message:
            return HttpResponse(
                f'<p class="text-red-500 text-xs mt-1">{error_message}</p>'
            )
        else:
            return HttpResponse('<p class="text-green-600 text-xs mt-1">✓</p>')


# HTMX Validation CBV for the 'username' field in signup.html
class ValidateUsernameView(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get("username", "").strip()
        error_message = ""

        if not username:
            error_message = _("Username cannot be empty.")
        elif len(username) < 3:
            error_message = _("Username must be at least 3 characters.")
        elif User.objects.filter(username__iexact=username).exists():
            error_message = _("This username is already taken.")

        if error_message:
            return HttpResponse(
                f'<p class="text-red-500 text-xs mt-1">{error_message}</p>'
            )
        else:
            return HttpResponse('<p class="text-green-600 text-xs mt-1">✓</p>')


# HTMX Validation CBV for the 'email' field in signup.html
class ValidateEmailView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip()
        error_message = ""

        if not email:
            error_message = _("Email cannot be empty.")
        else:
            try:
                django_validate_email(email)
            except ValidationError:
                error_message = _("Please enter a valid email address.")

            if not error_message and User.objects.filter(email__iexact=email).exists():
                error_message = _("This email is already registered.")

        if error_message:
            return HttpResponse(
                f'<p class="text-red-500 text-xs mt-1">{error_message}</p>'
            )
        else:
            return HttpResponse('<p class="text-green-600 text-xs mt-1">✓</p>')


# HTMX Validation CBV for the 'password' field in signup.html
class ValidatePasswordView(View):
    def post(self, request, *args, **kwargs):
        password = request.POST.get("password", "").strip()
        error_message = ""

        if not password:
            error_message = _("Password cannot be empty.")
        elif len(password) < 8:
            error_message = _("Password must be at least 8 characters long.")
        # Add more password strength rules here if needed

        if error_message:
            return HttpResponse(
                f'<p class="text-red-500 text-xs mt-1">{error_message}</p>'
            )
        else:
            return HttpResponse('<p class="text-green-600 text-xs mt-1">✓</p>')


# HTMX Validation CBV for the 'password2' (password confirmation) field in signup.html
class ValidatePassword2View(View):
    def post(self, request, *args, **kwargs):
        password = request.POST.get("password", "").strip()
        password2 = request.POST.get("password2", "").strip()
        error_message = ""

        if not password2:
            error_message = _("Confirmation password cannot be empty.")
        elif password != password2:
            error_message = _("Passwords do not match.")

        if error_message:
            return HttpResponse(
                f'<p class="text-red-500 text-xs mt-1">{error_message}</p>'
            )
        else:
            return HttpResponse('<p class="text-green-600 text-xs mt-1">✓</p>')


# Existing views (unchanged in this optimization step)
class MobileMenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "partials/mobile_menu.html")


class CustomPasswordResetView(FormView):
    template_name = "account/password_reset.html"
    form_class = CustomPasswordResetRequestForm
    success_url = reverse_lazy("users:password_reset_done")
    token_generator = default_token_generator

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email__iexact=email)
            send_password_reset_email_task.delay(user.pk)
        except User.DoesNotExist:
            pass  # Fail silently for security reasons
        return super().form_valid(form)


class CustomPasswordResetDoneView(TemplateView):
    template_name = "account/password_reset_done.html"


class CustomPasswordResetConfirmView(FormView):
    template_name = "account/password_reset_confirm.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("users:password_reset_complete")


class CustomPasswordResetCompleteView(TemplateView):
    template_name = "account/password_reset_complete.html"


class AccountOverviewView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/detail.html"


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    แสดงฟอร์มสำหรับให้ผู้ใช้แก้ไขข้อมูลส่วนตัว
    """

    model = User
    form_class = UserProfileUpdateForm
    template_name = "profiles/update.html"  # เราจะสร้าง Template นี้ในขั้นตอนต่อไป
    success_message = _("Your profile was updated successfully")
    success_url = reverse_lazy("account:overview")

    def get_object(self):
        # ให้ View นี้แก้ไขข้อมูลของ User ที่ Login อยู่เสมอ
        return self.request.user


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})
