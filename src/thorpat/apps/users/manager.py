from django.contrib.auth.models import BaseUserManager


class UserAdminManager(BaseUserManager):
    def create_user(self, username, email, password, is_active=True, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            is_active=is_active,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        u = self.create_user(username, email, password=password, **extra_fields)
        u.is_admin = True
        u.is_staff = True
        u.is_superuser = True
        u.save(using=self._db)
        return u
