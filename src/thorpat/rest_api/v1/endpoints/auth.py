import logging

from django.contrib.auth import authenticate
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from thorpat.apps.users.models import User

# New schema imports
from thorpat.rest_api.schemas.auth import (
    MessageResponseSchema,
    PasswordResetConfirmSchema,
    PasswordResetRequestSchema,
    UserRegisterSchema,
)
from thorpat.rest_api.schemas.base_schemas import BaseResponse
from thorpat.rest_api.schemas.token import LoginSchema, TokenResponseSchema
from thorpat.rest_api.schemas.users import UserSchema  # For returning user data
from thorpat.rest_api.utils import (
    account_activation_token,  # Import the generator instance
    generate_access_token,
    generate_refresh_token,
    password_reset_token_generator,  # Import the generator instance
    send_confirmation_email,
    send_password_reset_email,
    validate_user_token,
)

log = logging.getLogger(__name__)
router = Router(tags=["authentication"], auth=None)  # auth=None for public endpoints


# Existing login endpoint
@router.post("/login", response=BaseResponse[TokenResponseSchema])
def login(request: HttpRequest, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    log.info(f"Login attempt for user: {data.username}")
    log.debug(
        f"Authenticated user: {User.objects.filter(username=data.username).first()}"
    )

    log.info(f"User {user} logged in")
    log.debug(f"User object: {user is not None}")  # Log the user object for debugging
    if user is not None:
        log.debug(f"User is: {user.is_active}")  # Log the user object for debugging
        if not user.is_active:  # Check if user is active (email confirmed)
            raise HttpError(
                403, "Account not activated. Please check your email to confirm."
            )
        access_token = generate_access_token(user)
        refresh_token_str = generate_refresh_token(user)
        return BaseResponse(
            success=True,
            message="Login successful",
            data=TokenResponseSchema(
                access_token=access_token,
                refresh_token=refresh_token_str,
            ),
        )
    raise HttpError(401, "Invalid username or password or account not activated.")


@router.post(
    "/register", response=BaseResponse[UserSchema], summary="Register a new user"
)
def register_user(
    request: HttpRequest, data: UserRegisterSchema
):  # data จะถูก validate โดย Pydantic ก่อน
    # ไม่จำเป็นต้องเช็ค password confirmation ที่นี่อีกแล้ว
    # ถ้า password ไม่ตรงกัน Pydantic จะ raise error และส่ง 422 response ไปแล้ว

    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username already exists.")
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email already registered.")
    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password,  # ใช้ password ที่ผ่านการ validate แล้ว
        first_name=data.first_name or "",
        last_name=data.last_name or "",
        is_active=False,
    )
    send_confirmation_email(request, user)

    return BaseResponse(
        success=True,
        message="Registration successful. Please check your email to confirm your account.",
        data=UserSchema.from_orm(user),
    )


# Option 1: POST endpoint for email confirmation (if token is complex or long)
@router.post(
    "/confirm-email",
    response=BaseResponse[MessageResponseSchema],
    summary="Confirm user email",
)
def confirm_email_post(
    request: HttpRequest, uidb64: str, token: str
):  # Or use EmailConfirmationSchema if preferred
    user = validate_user_token(uidb64, token, account_activation_token)
    if user is not None:
        if user.is_active:
            return BaseResponse(success=True, message="Account already activated.")
        user.is_active = True
        user.save()
        return BaseResponse(
            success=True, message="Email confirmed successfully. You can now log in."
        )
    raise HttpError(400, "Invalid confirmation link or token.")


# Option 2: GET endpoint for email confirmation (more common for links in emails)
# This would also require adding this to urls.py if not using Ninja for the whole path
# For Ninja, we can define it like this:
@router.get(
    "/confirm-email/{uidb64}/{token}",
    response=BaseResponse[MessageResponseSchema],
    summary="Confirm user email via link",
)
def confirm_email_get(request: HttpRequest, uidb64: str, token: str):
    user = validate_user_token(uidb64, token, account_activation_token)
    if user is not None:
        if user.is_active:
            return BaseResponse(
                success=True, data={"message": "Account already activated."}
            )  # Using data for Ninja compatibility
        user.is_active = True
        user.save()
        return BaseResponse(
            success=True,
            data={"message": "Email confirmed successfully. You can now log in."},
        )
    raise HttpError(400, "Invalid confirmation link or token.")


@router.post(
    "/password-reset-request",
    response=BaseResponse[MessageResponseSchema],
    summary="Request password reset",
)
def password_reset_request(request: HttpRequest, data: PasswordResetRequestSchema):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        # Do not reveal that the user doesn't exist for security reasons
        # Log this event for admin review if necessary
        log.warning(f"Password reset requested for non-existent email: {data.email}")
        return BaseResponse(
            success=True,
            message="If an account with this email exists, a password reset link has been sent.",
        )

    send_password_reset_email(request, user)
    return BaseResponse(
        success=True,
        message="If an account with this email exists, a password reset link has been sent.",
    )


@router.post(
    "/password-reset-confirm",
    response=BaseResponse[MessageResponseSchema],
    summary="Confirm password reset",
)
def password_reset_confirm(
    request: HttpRequest, data: PasswordResetConfirmSchema, uidb64: str
):
    user = validate_user_token(uidb64, data.token, password_reset_token_generator)
    if user is not None:
        # Django's set_password handles hashing.
        # Password validation (e.g., against common passwords) can be added here or in the User model.
        # Django's AUTH_PASSWORD_VALIDATORS will be checked if you save the user through a form,
        # but for direct set_password, they are not automatically applied unless you call validate_password.
        # from django.contrib.auth.password_validation import validate_password
        # try:
        #     validate_password(data.new_password, user=user)
        # except django_ValidationError as e:
        #     raise HttpError(400, {"detail": list(e.messages)}) from e

        user.set_password(data.new_password)  # ใช้ new_password ที่ผ่านการ validate แล้ว
        if not user.is_active:
            user.is_active = True
        user.save()
        return BaseResponse(
            success=True, message="Password has been reset successfully."
        )
    raise HttpError(400, "Invalid reset link or token.")
