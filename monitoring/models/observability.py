import psutil
from django.db import models
from django.utils import timezone

from common.models import BaseModel


class CodeLog(BaseModel):
    LEVEL_CHOICES = [
        ("DEBUG", "Debug"),
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
        ("ACTION_LOG", "ActionLog"),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default="INFO")
    module = models.CharField(
        max_length=100
    )  # Name of the module or file where the log originates
    method = models.CharField(max_length=100, blank=True)  # Method or function name
    message = models.TextField()  # The log message content
    context = models.JSONField(
        null=True, blank=True
    )  # Any additional context (e.g., function parameters, status data)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(null=True, blank=True)  # Execution time, if relevant
    cpu_usage = models.FloatField(null=True, blank=True)  # Field to store CPU usage
    memory_usage = models.FloatField(null=True, blank=True)

    user = models.ForeignKey(
        "account.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["level"]),
            models.Index(fields=["module", "method"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.level} - {self.module} - {self.method} - {self.timestamp}"

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
    ):
        """
        Utility method for logging messages in the CodeLog model with CPU and memory usage.
        """
        cls.objects.create(
            level=level,
            module=module,
            method=method,
            message=message,
            context=context,
            user=user,
            duration=duration,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
        )

    @classmethod
    def log_debug(cls, module, method, message, context=None, duration=None):
        cpu_usage, memory_usage = cls._get_system_usage()
        cls.log_message(
            "DEBUG", module, method, message, context, duration, cpu_usage, memory_usage
        )

    @classmethod
    def log_info(cls, module, method, message, context=None, duration=None):
        cpu_usage, memory_usage = cls._get_system_usage()
        cls.log_message(
            "INFO", module, method, message, context, duration, cpu_usage, memory_usage
        )

    @classmethod
    def log_warning(cls, module, method, message, context=None, duration=None):
        cpu_usage, memory_usage = cls._get_system_usage()
        cls.log_message(
            "WARNING",
            module,
            method,
            message,
            context,
            duration,
            cpu_usage,
            memory_usage,
        )

    @classmethod
    def log_error(cls, module, method, message, context=None, duration=None):
        cpu_usage, memory_usage = cls._get_system_usage()
        cls.log_message(
            "ERROR", module, method, message, context, duration, cpu_usage, memory_usage
        )

    @classmethod
    def log_critical(cls, module, method, message, context=None, duration=None):
        cpu_usage, memory_usage = cls._get_system_usage()
        cls.log_message(
            "CRITICAL",
            module,
            method,
            message,
            context,
            duration,
            cpu_usage,
            memory_usage,
        )

    @classmethod
    def log_client(
        cls, module, method, message, context=None, user=None, duration=None
    ):
        cpu_usage, memory_usage = cls._get_system_usage()
        cls.log_message(
            "ACTION_LOG",
            module,
            method,
            message,
            context,
            user,
            duration,
            cpu_usage,
            memory_usage,
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
