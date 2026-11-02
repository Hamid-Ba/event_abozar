"""
خروجی CSV برای پنل مدیریت
UTF-8 با BOM تا فارسی در اکسل درست باز شود
"""
import csv

from django.http import HttpResponse


def _safe(value):
    """جلوگیری از اجرای فرمول در اکسل (CSV injection) برای مقادیر متنی کاربر"""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def csv_response(filename, header, rows):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write("﻿")
    writer = csv.writer(response)
    writer.writerow(header)
    for row in rows:
        writer.writerow([_safe(v) for v in row])
    return response
