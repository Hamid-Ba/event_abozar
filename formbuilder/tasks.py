"""
Celery tasks
"""
from celery import shared_task
from django.utils import timezone

from festival.models import Notification
from formbuilder.access import eligible_users, open_surveys


@shared_task
def notify_opened_forms():
    """
    برای هر نظرسنجی که تازه باز شده (و هنوز اعلانش نرفته) به مخاطبانش اعلان درون‌برنامه می‌فرستد.
    باید در django-celery-beat (ادمین ← Periodic tasks) هر چند دقیقه یک‌بار زمان‌بندی شود:
    formbuilder.tasks.notify_opened_forms
    """
    sent = 0
    for form in open_surveys().filter(notified_at__isnull=True):
        notifications = [
            Notification(
                user=user,
                kind=Notification.KIND_FORM_OPENED,
                title="نظرسنجی جدید",
                body=f"نظرسنجی «{form.title}» باز شد. خوشحال می‌شویم نظر شما را بدانیم.",
                object_id=form.id,
            )
            for user in eligible_users(form)
        ]
        Notification.objects.bulk_create(notifications)
        form.notified_at = timezone.now()
        form.save(update_fields=["notified_at"])
        sent += len(notifications)
    return sent
