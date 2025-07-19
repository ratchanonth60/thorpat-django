from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from thorpat.tasks.email import send_activation_email_task

User = get_user_model()


@receiver(post_save, sender=User)
def send_confirmation_email_on_user_creation(sender, instance, created, **kwargs):
    """
    Sends a confirmation email when a new user is created.
    """
    # เช็คว่าเป็นการ "สร้าง" object ใหม่จริงๆ (ไม่ใช่การ update)
    if created:
        # สั่งให้ Celery Task ทำงานในเบื้องหลัง
        # .delay() คือคำสั่งมาตรฐานในการเรียกใช้ Celery Task
        send_activation_email_task.delay(instance.pk)  # type: ignore[call-arg]
        print(f"Confirmation email task queued for user {instance.email}")
