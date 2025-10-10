#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append("/Users/hamidba/Documents/DjangoProjects/event_abozar")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from content.models import News, Education, Event
from django.utils import timezone

# Create sample news
news1 = News.objects.create(
    title="اخبار مهم جشنواره ابوذر",
    description="یازدهمین جشنواره رسانه‌ای ابوذر با حضور فعالان رسانه‌ای برگزار خواهد شد.",
    publish_date=timezone.now().date(),
)
news1.tags.add("جشنواره", "اخبار", "رسانه")

news2 = News.objects.create(
    title="اعلام زمان ثبت‌نام",
    description="زمان ثبت‌نام برای شرکت در جشنواره اعلام شد.",
    publish_date=timezone.now().date(),
)
news2.tags.add("ثبت‌نام", "اطلاعیه")

# Create sample education content
edu1 = Education.objects.create(
    title="آموزش تولید محتوای رسانه‌ای",
    description="دوره جامع آموزش تولید محتوای با کیفیت برای رسانه‌های مختلف.",
    publish_date=timezone.now().date(),
)
edu1.tags.add("آموزش", "تولید محتوا", "رسانه")

edu2 = Education.objects.create(
    title="تکنیک‌های فیلمسازی",
    description="آموزش تکنیک‌های پیشرفته فیلمسازی برای مبتدیان و حرفه‌ای‌ها.",
    publish_date=timezone.now().date(),
)
edu2.tags.add("فیلمسازی", "آموزش", "تکنیک")

# Create sample events
event1 = Event.objects.create(
    title="مراسم افتتاحیه جشنواره",
    description="مراسم افتتاحیه یازدهمین جشنواره رسانه‌ای ابوذر.",
    publish_date=timezone.now().date(),
)
event1.tags.add("افتتاحیه", "مراسم", "رویداد")

event2 = Event.objects.create(
    title="نشست تخصصی رسانه",
    description="نشست تخصصی پیرامون آینده رسانه‌های دیجیتال.",
    publish_date=timezone.now().date(),
)
event2.tags.add("نشست", "رسانه دیجیتال", "تخصصی")

print(f"Successfully created:")
print(f"- {News.objects.count()} news items")
print(f"- {Education.objects.count()} education items")
print(f"- {Event.objects.count()} events")
