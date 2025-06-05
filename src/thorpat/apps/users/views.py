from django.contrib.auth import get_user_model  # Recommended way to get User model
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

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


# +++++++++++++ END OF ADDED VIEWS ++++++++++++++
