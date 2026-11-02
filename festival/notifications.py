"""
ساخت اعلان‌ها. امتیاز و نتیجهٔ داوری هرگز در متن اعلان نمی‌آید.
"""
from festival.models import Notification, Work

WORK_STATUS_MESSAGES = {
    Work.STATUS_SUBMITTED: ("اثر شما ثبت شد", "اثر «{title}» با موفقیت ثبت شد."),
    Work.STATUS_UNDER_REVIEW: (
        "اثر شما وارد مرحله داوری شد",
        "داوری اثر «{title}» آغاز شده است.",
    ),
    Work.STATUS_JUDGED: (
        "داوری اثر شما به پایان رسید",
        "داوری اثر «{title}» تکمیل شد. نتیجه از طریق دبیرخانه اعلام می‌شود.",
    ),
}


def notify_work_status(work):
    message = WORK_STATUS_MESSAGES.get(work.status)
    # بازگشت اثر به «ارسال‌شده» به‌دلیل حذف امتیاز توسط مدیر، اعلان نمی‌خواهد
    if message is None or work.status == Work.STATUS_SUBMITTED:
        return None
    title, body = message
    return Notification.objects.create(
        user=work.festival_registration.user,
        kind=Notification.KIND_WORK_STATUS,
        title=title,
        body=body.format(title=work.title),
        object_id=work.pk,
    )
