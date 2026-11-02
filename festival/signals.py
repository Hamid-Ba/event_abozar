"""
بعد از هر ثبت/ویرایش/حذف امتیاز (از هر راهی، از جمله ادمین) امتیاز نهایی و وضعیت اثر دوباره حساب می‌شود
"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from festival.models import Review, Work


@receiver(post_save, sender=Review)
def review_saved(sender, instance, **kwargs):
    instance.work.recalculate_scores()


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    work = Work.objects.filter(pk=instance.work_id).first()
    if work is not None:
        work.recalculate_scores()
