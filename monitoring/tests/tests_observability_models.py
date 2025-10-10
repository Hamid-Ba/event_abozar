from model_bakery import baker

from datetime import timedelta
from django.test import TestCase
from django.utils import timezone


from ..models import *


class CodeLogModelTest(TestCase):
    def test_log_creation(self):
        """
        Test that a CodeLog entry is created with correct attributes.
        """
        # Call log_message to create the log entry
        CodeLog.log_message(
            level="INFO",
            module="my_module",
            method="my_method",
            message="This is an informational log message.",
            context={"key": "value"},
            duration=0.123,
        )

        # Retrieve the latest log entry
        log_entry = CodeLog.objects.latest("timestamp")

        # Check that log entry was created successfully and has correct attributes
        self.assertIsNotNone(log_entry.id)
        self.assertEqual(log_entry.level, "INFO")
        self.assertEqual(log_entry.module, "my_module")
        self.assertEqual(log_entry.method, "my_method")
        self.assertEqual(log_entry.message, "This is an informational log message.")
        self.assertEqual(log_entry.context, {"key": "value"})
        self.assertAlmostEqual(log_entry.duration, 0.123, places=3)

    def test_log_entry_timestamps(self):
        """
        Test that the timestamp is set correctly on creation.
        """
        now = timezone.now()
        CodeLog.log_info(
            module="test_module",
            method="test_method",
            message="Testing timestamp logging.",
        )

        # Retrieve the latest log entry
        log_entry = CodeLog.objects.latest("timestamp")

        # Assert that the timestamp is close to the current time
        self.assertTrue((timezone.now() - log_entry.timestamp).total_seconds() < 1)

    def test_log_query_by_level(self):
        """
        Test that logs can be filtered by level.
        """
        CodeLog.log_info(
            module="test_module", method="test_method", message="Info log."
        )
        CodeLog.log_error(
            module="test_module", method="test_method", message="Error log."
        )

        info_logs = CodeLog.objects.filter(level="INFO")
        error_logs = CodeLog.objects.filter(level="ERROR")

        # Verify only the correct logs are returned
        self.assertEqual(info_logs.count(), 1)
        self.assertEqual(error_logs.count(), 1)
        self.assertEqual(info_logs.first().message, "Info log.")
        self.assertEqual(error_logs.first().message, "Error log.")

    def test_logging_methods(self):
        """
        Test the helper logging methods (log_debug, log_info, etc.).
        """
        CodeLog.log_debug("test_module", "test_debug_method", "Debug message")
        CodeLog.log_critical("test_module", "test_critical_method", "Critical message")

        # Verify correct log level and message
        debug_log = CodeLog.objects.get(level="DEBUG")
        critical_log = CodeLog.objects.get(level="CRITICAL")

        self.assertEqual(debug_log.message, "Debug message")
        self.assertEqual(critical_log.message, "Critical message")

    def test_expensive_operation_logging_with_duration(self):
        """
        Test logging an operation that records a duration.
        """
        CodeLog.log_message(
            level="INFO",
            module="test_module",
            method="expensive_operation",
            message="Logging an expensive operation",
            duration=2.35,
        )

        # Verify duration is logged correctly
        log_entry = CodeLog.objects.get(method="expensive_operation")
        self.assertAlmostEqual(log_entry.duration, 2.35)


class NotificationModelTest(TestCase):
    def setUp(self):
        # Create a user instance
        self.user = baker.make("account.User", phone="09151498722")

    def test_create_notification(self):
        # Create a notification instance
        notification = Notification.objects.create(
            title="Test Notification",
            message="This is a test message",
            channel="sms",
            priority="high",
            user=self.user,
        )

        # Check if the notification is created with the correct attributes
        self.assertEqual(notification.title, "Test Notification")
        self.assertEqual(notification.message, "This is a test message")
        self.assertEqual(notification.channel, "sms")
        self.assertEqual(notification.priority, "high")
        self.assertEqual(notification.is_read, False)

    def test_mark_as_read(self):
        # Create a notification and mark it as read
        notification = Notification.objects.create(
            title="Unread Notification",
            message="Message content",
            channel="dashboard",
            user=self.user,
        )

        # Mark as read and save
        notification.mark_as_read()

        # Check if the notification is marked as read
        self.assertTrue(notification.is_read)

    def test_is_expired(self):
        # Create an expired notification
        expired_notification = Notification.objects.create(
            title="Expired Notification",
            message="Message content",
            channel="dashboard",
            user=self.user,
            expiration_date=timezone.now() - timedelta(days=1),
        )

        # Create a non-expired notification
        active_notification = Notification.objects.create(
            title="Active Notification",
            message="Message content",
            channel="dashboard",
            user=self.user,
            expiration_date=timezone.now() + timedelta(days=1),
        )

        # Check expiration status
        self.assertTrue(expired_notification.is_expired)
        self.assertFalse(active_notification.is_expired)

    def test_string_representation(self):
        notification = Notification.objects.create(
            title="String Representation Test",
            message="Testing __str__ method",
            channel="sms",
            priority="medium",
            user=self.user,
        )

        # Check __str__ output
        expected_str = f"{self.user} - sms - medium"
        self.assertEqual(str(notification), expected_str)
