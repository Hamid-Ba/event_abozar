import psutil
import traceback
import sys
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from common.models import BaseModel


class CodeLog(BaseModel):
    """Enhanced CodeLog model for comprehensive logging and exception monitoring"""

    LEVEL_CHOICES = [
        ("DEBUG", "اشکال‌زدایی"),
        ("INFO", "اطلاعات"),
        ("WARNING", "هشدار"),
        ("ERROR", "خطا"),
        ("CRITICAL", "خطای بحرانی"),
        ("ACTION_LOG", "لاگ عملیات"),
        ("EXCEPTION", "استثنا"),
        ("SECURITY", "امنیتی"),
        ("PERFORMANCE", "عملکرد"),
    ]

    # Log type categorization
    LOG_TYPE_CHOICES = [
        ("SYSTEM", "سیستم"),
        ("USER_ACTION", "عملیات کاربر"),
        ("API_CALL", "فراخوانی API"),
        ("DATABASE", "پایگاه داده"),
        ("AUTHENTICATION", "احراز هویت"),
        ("AUTHORIZATION", "مجوز دسترسی"),
        ("VALIDATION", "اعتبارسنجی"),
        ("EXCEPTION", "استثنا"),
        ("PERFORMANCE", "عملکرد"),
        ("SECURITY", "امنیت"),
    ]

    # Enhanced fields with Persian verbose names
    level = models.CharField(
        max_length=15,
        choices=LEVEL_CHOICES,
        default="INFO",
        verbose_name="سطح لاگ",
        help_text="سطح اهمیت لاگ",
    )

    log_type = models.CharField(
        max_length=20,
        choices=LOG_TYPE_CHOICES,
        default="SYSTEM",
        verbose_name="نوع لاگ",
        help_text="دسته‌بندی نوع لاگ",
    )

    module = models.CharField(
        max_length=100, verbose_name="ماژول", help_text="نام ماژول یا فایل مبدأ لاگ"
    )

    method = models.CharField(
        max_length=100, blank=True, verbose_name="متد", help_text="نام متد یا تابع"
    )

    message = models.TextField(verbose_name="پیام", help_text="متن پیام لاگ")

    context = models.JSONField(
        null=True,
        blank=True,
        verbose_name="زمینه",
        help_text="اطلاعات اضافی (پارامترها، وضعیت، و غیره)",
    )

    # Exception handling fields
    exception_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="نوع استثنا",
        help_text="نوع استثنای رخ داده",
    )

    exception_message = models.TextField(
        blank=True, null=True, verbose_name="پیام استثنا", help_text="پیام خطای استثنا"
    )

    traceback_info = models.TextField(
        blank=True,
        null=True,
        verbose_name="جزئیات traceback",
        help_text="اطلاعات کامل traceback",
    )

    # Request information
    request_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="مسیر درخواست",
        help_text="مسیر URL درخواست",
    )

    request_method = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="روش درخواست",
        help_text="نوع HTTP method (GET, POST, etc.)",
    )

    ip_address = models.GenericIPAddressField(
        blank=True, null=True, verbose_name="آدرس IP", help_text="آدرس IP کاربر"
    )

    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="اطلاعات مرورگر کاربر",
    )

    # Timing and performance
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="زمان ثبت", help_text="زمان ثبت لاگ"
    )

    duration = models.FloatField(
        null=True, blank=True, verbose_name="مدت اجرا", help_text="زمان اجرا به ثانیه"
    )

    # System resources
    cpu_usage = models.FloatField(
        null=True, blank=True, verbose_name="مصرف CPU", help_text="درصد مصرف پردازنده"
    )

    memory_usage = models.FloatField(
        null=True, blank=True, verbose_name="مصرف حافظه", help_text="درصد مصرف حافظه"
    )

    # User information
    user = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="کاربر",
        help_text="کاربر مرتبط با این لاگ",
    )

    # Additional flags
    is_resolved = models.BooleanField(
        default=False, verbose_name="حل شده", help_text="آیا این مسئله حل شده است؟"
    )

    resolution_note = models.TextField(
        blank=True,
        null=True,
        verbose_name="یادداشت حل مسئله",
        help_text="توضیحات مربوط به حل مسئله",
    )

    tags = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="برچسب‌ها",
        help_text="برچسب‌های مفید برای جستجو (با کاما جدا کنید)",
    )

    class Meta:
        verbose_name = "لاگ سیستم"
        verbose_name_plural = "لاگ‌های سیستم"
        indexes = [
            models.Index(fields=["level"]),
            models.Index(fields=["log_type"]),
            models.Index(fields=["module", "method"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["user"]),
            models.Index(fields=["exception_type"]),
            models.Index(fields=["is_resolved"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.get_level_display()} - {self.module} - {self.method} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_exception(self):
        """Check if this log entry is an exception"""
        return self.level == "EXCEPTION" or self.exception_type is not None

    @property
    def is_error_level(self):
        """Check if this is an error-level log"""
        return self.level in ["ERROR", "CRITICAL", "EXCEPTION"]

    @property
    def severity_score(self):
        """Return a severity score for prioritization"""
        severity_map = {
            "DEBUG": 1,
            "INFO": 2,
            "WARNING": 3,
            "ERROR": 4,
            "CRITICAL": 5,
            "EXCEPTION": 5,
            "SECURITY": 5,
            "PERFORMANCE": 3,
        }
        return severity_map.get(self.level, 2)

    @classmethod
    def log_message(
        cls,
        level,
        module,
        method,
        message,
        context=None,
        user=None,
        duration=None,
        cpu_usage=None,
        memory_usage=None,
        log_type="SYSTEM",
        request=None,
        exception=None,
        tags=None,
    ):
        """
        Enhanced utility method for comprehensive logging with exception handling.
        """
        # Auto-detect system usage if not provided
        if cpu_usage is None or memory_usage is None:
            auto_cpu, auto_memory = cls._get_system_usage()
            cpu_usage = cpu_usage or auto_cpu
            memory_usage = memory_usage or auto_memory

        # Extract request information if available
        request_path = None
        request_method = None
        ip_address = None
        user_agent = None

        if request:
            request_path = request.path
            request_method = request.method
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            # Get user from request if not provided
            if not user and hasattr(request, "user") and request.user.is_authenticated:
                user = request.user

        # Handle exception information
        exception_type = None
        exception_message = None
        traceback_info = None

        if exception:
            exception_type = type(exception).__name__
            exception_message = str(exception)
            traceback_info = traceback.format_exc()
            # Auto-set level to EXCEPTION if not already error-level
            if level not in ["ERROR", "CRITICAL", "EXCEPTION"]:
                level = "EXCEPTION"
            # Auto-set log_type
            if log_type == "SYSTEM":
                log_type = "EXCEPTION"

        return cls.objects.create(
            level=level,
            log_type=log_type,
            module=module,
            method=method,
            message=message,
            context=context,
            user=user,
            duration=duration,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            request_path=request_path,
            request_method=request_method,
            ip_address=ip_address,
            user_agent=user_agent,
            exception_type=exception_type,
            exception_message=exception_message,
            traceback_info=traceback_info,
            tags=tags,
        )

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    # Enhanced logging methods with exception handling
    @classmethod
    def log_debug(
        cls,
        module,
        method,
        message,
        context=None,
        duration=None,
        request=None,
        user=None,
        tags=None,
    ):
        """Log debug information"""
        return cls.log_message(
            "DEBUG",
            module,
            method,
            message,
            context=context,
            duration=duration,
            request=request,
            user=user,
            log_type="SYSTEM",
            tags=tags,
        )

    @classmethod
    def log_info(
        cls,
        module,
        method,
        message,
        context=None,
        duration=None,
        request=None,
        user=None,
        tags=None,
    ):
        """Log general information"""
        return cls.log_message(
            "INFO",
            module,
            method,
            message,
            context=context,
            duration=duration,
            request=request,
            user=user,
            log_type="SYSTEM",
            tags=tags,
        )

    @classmethod
    def log_warning(
        cls,
        module,
        method,
        message,
        context=None,
        duration=None,
        request=None,
        user=None,
        tags=None,
    ):
        """Log warning messages"""
        return cls.log_message(
            "WARNING",
            module,
            method,
            message,
            context=context,
            duration=duration,
            request=request,
            user=user,
            log_type="SYSTEM",
            tags=tags,
        )

    @classmethod
    def log_error(
        cls,
        module,
        method,
        message,
        context=None,
        duration=None,
        request=None,
        user=None,
        exception=None,
        tags=None,
    ):
        """Log error messages with optional exception details"""
        return cls.log_message(
            "ERROR",
            module,
            method,
            message,
            context=context,
            duration=duration,
            request=request,
            user=user,
            exception=exception,
            log_type="SYSTEM",
            tags=tags,
        )

    @classmethod
    def log_critical(
        cls,
        module,
        method,
        message,
        context=None,
        duration=None,
        request=None,
        user=None,
        exception=None,
        tags=None,
    ):
        """Log critical errors with optional exception details"""
        return cls.log_message(
            "CRITICAL",
            module,
            method,
            message,
            context=context,
            duration=duration,
            request=request,
            user=user,
            exception=exception,
            log_type="SYSTEM",
            tags=tags,
        )

    @classmethod
    def log_exception(
        cls,
        module,
        method,
        message,
        exception,
        context=None,
        request=None,
        user=None,
        tags=None,
    ):
        """Log exceptions with full traceback information"""
        return cls.log_message(
            "EXCEPTION",
            module,
            method,
            message,
            context=context,
            request=request,
            user=user,
            exception=exception,
            log_type="EXCEPTION",
            tags=tags,
        )

    @classmethod
    def log_user_action(
        cls,
        module,
        method,
        message,
        user,
        context=None,
        duration=None,
        request=None,
        tags=None,
    ):
        """Log user actions for audit trail"""
        return cls.log_message(
            "ACTION_LOG",
            module,
            method,
            message,
            context=context,
            user=user,
            duration=duration,
            request=request,
            log_type="USER_ACTION",
            tags=tags,
        )

    @classmethod
    def log_api_call(
        cls,
        module,
        method,
        message,
        context=None,
        duration=None,
        request=None,
        user=None,
        tags=None,
    ):
        """Log API calls and responses"""
        return cls.log_message(
            "INFO",
            module,
            method,
            message,
            context=context,
            duration=duration,
            request=request,
            user=user,
            log_type="API_CALL",
            tags=tags,
        )

    @classmethod
    def log_security_event(
        cls, module, method, message, context=None, request=None, user=None, tags=None
    ):
        """Log security-related events"""
        return cls.log_message(
            "SECURITY",
            module,
            method,
            message,
            context=context,
            request=request,
            user=user,
            log_type="SECURITY",
            tags=tags,
        )

    @classmethod
    def log_performance(
        cls,
        module,
        method,
        message,
        duration,
        context=None,
        request=None,
        user=None,
        tags=None,
    ):
        """Log performance metrics"""
        return cls.log_message(
            "PERFORMANCE",
            module,
            method,
            message,
            context=context,
            duration=duration,
            request=request,
            user=user,
            log_type="PERFORMANCE",
            tags=tags,
        )

    @classmethod
    def log_database_operation(
        cls, module, method, message, context=None, duration=None, user=None, tags=None
    ):
        """Log database operations"""
        return cls.log_message(
            "INFO",
            module,
            method,
            message,
            context=context,
            duration=duration,
            user=user,
            log_type="DATABASE",
            tags=tags,
        )

    @classmethod
    def log_authentication(
        cls, module, method, message, user=None, context=None, request=None, tags=None
    ):
        """Log authentication events"""
        return cls.log_message(
            "INFO",
            module,
            method,
            message,
            context=context,
            request=request,
            user=user,
            log_type="AUTHENTICATION",
            tags=tags,
        )

    @staticmethod
    def _get_system_usage():
        """
        Utility function to get the current CPU and memory usage.
        Returns a tuple (cpu_usage, memory_usage).
        """
        cpu_usage = psutil.cpu_percent(interval=0.1)  # Get CPU usage
        memory_usage = psutil.virtual_memory().percent  # Get memory usage
        return cpu_usage, memory_usage


class Notification(BaseModel):
    CHANNEL_CHOICES = [
        ("sms", "SMS"),
        ("dashboard", "Dashboard"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    title = models.CharField(max_length=100)
    message = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="low")
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True, blank=True)

    user = models.ForeignKey(
        "account.User", on_delete=models.CASCADE, related_name="notifications"
    )

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ["-priority", "-timestamp"]

    def __str__(self):
        return f"{self.user} - {self.channel} - {self.priority}"

    def send_notification(self):
        """
        Sends the notification through the specified channel.
        """
        if self.channel == "sms":
            self.send_sms()
        elif self.channel == "dashboard":
            self.send_dashboard_notification()

    def send_sms(self):
        # Logic to send SMS (e.g., through an API)
        pass

    def send_dashboard_notification(self):
        # Logic to show notification in user dashboard
        pass

    def mark_as_read(self):
        """
        Marks the notification as read.
        """
        self.is_read = True
        self.save()

    @property
    def is_expired(self):
        """
        Checks if the notification is expired based on the expiration date.
        """
        return self.expiration_date and timezone.now() > self.expiration_date
