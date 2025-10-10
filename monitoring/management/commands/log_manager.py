"""
Management command for log analysis and maintenance
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from monitoring.models import CodeLog


class Command(BaseCommand):
    help = "مدیریت و تجزیه و تحلیل لاگ‌های سیستم"

    def add_arguments(self, parser):
        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="پاک کردن لاگ‌های قدیمی (بیش از 30 روز)",
        )

        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="تعداد روزهای نگهداری لاگ (پیش‌فرض: 30)",
        )

        parser.add_argument("--stats", action="store_true", help="نمایش آمار لاگ‌ها")

        parser.add_argument(
            "--critical", action="store_true", help="نمایش لاگ‌های بحرانی"
        )

        parser.add_argument(
            "--unresolved", action="store_true", help="نمایش مسائل حل نشده"
        )

        parser.add_argument("--export", type=str, help="صادرات لاگ‌ها به فایل CSV")

    def handle(self, *args, **options):
        if options["cleanup"]:
            self.cleanup_old_logs(options["days"])

        if options["stats"]:
            self.show_stats()

        if options["critical"]:
            self.show_critical_logs()

        if options["unresolved"]:
            self.show_unresolved_issues()

        if options["export"]:
            self.export_logs(options["export"])

        if not any(
            [
                options["cleanup"],
                options["stats"],
                options["critical"],
                options["unresolved"],
                options["export"],
            ]
        ):
            self.show_help()

    def cleanup_old_logs(self, days):
        """Clean up old logs"""
        cutoff_date = timezone.now() - timedelta(days=days)

        # Keep critical logs longer
        critical_logs = CodeLog.objects.filter(
            timestamp__lt=cutoff_date,
            level__in=["CRITICAL", "SECURITY", "EXCEPTION"],
            is_resolved=False,
        ).count()

        # Delete old non-critical logs
        deleted_count = (
            CodeLog.objects.filter(timestamp__lt=cutoff_date)
            .exclude(level__in=["CRITICAL", "SECURITY", "EXCEPTION"], is_resolved=False)
            .delete()[0]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ {deleted_count} لاگ قدیمی پاک شد. "
                f"{critical_logs} لاگ بحرانی حل نشده نگهداری شد."
            )
        )

    def show_stats(self):
        """Show log statistics"""
        total_logs = CodeLog.objects.count()

        # Stats by level
        level_stats = {}
        for level, display in CodeLog.LEVEL_CHOICES:
            count = CodeLog.objects.filter(level=level).count()
            if count > 0:
                level_stats[display] = count

        # Stats by type
        type_stats = {}
        for log_type, display in CodeLog.LOG_TYPE_CHOICES:
            count = CodeLog.objects.filter(log_type=log_type).count()
            if count > 0:
                type_stats[display] = count

        # Recent stats (last 24 hours)
        last_24h = timezone.now() - timedelta(hours=24)
        recent_logs = CodeLog.objects.filter(timestamp__gte=last_24h).count()
        recent_errors = CodeLog.objects.filter(
            timestamp__gte=last_24h, level__in=["ERROR", "CRITICAL", "EXCEPTION"]
        ).count()

        # Unresolved issues
        unresolved = CodeLog.objects.filter(
            level__in=["ERROR", "CRITICAL", "EXCEPTION"], is_resolved=False
        ).count()

        self.stdout.write(self.style.SUCCESS("📊 آمار لاگ‌های سیستم:"))
        self.stdout.write(f"  📝 کل لاگ‌ها: {total_logs}")
        self.stdout.write(f"  🕐 ۲۴ ساعت اخیر: {recent_logs}")
        self.stdout.write(f"  ⚠️  خطاهای اخیر: {recent_errors}")
        self.stdout.write(f"  🔴 مسائل حل نشده: {unresolved}")

        self.stdout.write("\n📈 آمار بر اساس سطح:")
        for level, count in level_stats.items():
            self.stdout.write(f"  • {level}: {count}")

        self.stdout.write("\n🏷️  آمار بر اساس نوع:")
        for log_type, count in type_stats.items():
            self.stdout.write(f"  • {log_type}: {count}")

    def show_critical_logs(self):
        """Show critical logs"""
        critical_logs = CodeLog.objects.filter(
            level__in=["CRITICAL", "ERROR", "EXCEPTION"]
        ).order_by("-timestamp")[:10]

        if not critical_logs:
            self.stdout.write(self.style.SUCCESS("✅ هیچ لاگ بحرانی یافت نشد."))
            return

        self.stdout.write(self.style.ERROR("🚨 لاگ‌های بحرانی اخیر:"))
        for log in critical_logs:
            status = "✅ حل شده" if log.is_resolved else "❌ حل نشده"
            self.stdout.write(
                f'  [{log.timestamp.strftime("%Y-%m-%d %H:%M")}] '
                f"{log.get_level_display()} - {log.module}.{log.method} "
                f"- {status}"
            )
            self.stdout.write(f"    📝 {log.message}")
            if log.exception_type:
                self.stdout.write(
                    f"    🐛 {log.exception_type}: {log.exception_message}"
                )
            self.stdout.write("")

    def show_unresolved_issues(self):
        """Show unresolved issues"""
        unresolved = CodeLog.objects.filter(
            level__in=["ERROR", "CRITICAL", "EXCEPTION"], is_resolved=False
        ).order_by("-timestamp")

        if not unresolved:
            self.stdout.write(self.style.SUCCESS("✅ همه مسائل حل شده‌اند."))
            return

        self.stdout.write(
            self.style.WARNING(f"⚠️  {unresolved.count()} مسئله حل نشده:")
        )

        for log in unresolved:
            self.stdout.write(
                f'  🔴 [{log.timestamp.strftime("%Y-%m-%d %H:%M")}] '
                f"{log.get_level_display()} - {log.module}.{log.method}"
            )
            self.stdout.write(f"     📝 {log.message}")
            if log.exception_type:
                self.stdout.write(f"     🐛 {log.exception_type}")
            self.stdout.write("")

    def export_logs(self, filename):
        """Export logs to CSV"""
        import csv

        logs = CodeLog.objects.all().order_by("-timestamp")[:1000]  # Last 1000 logs

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "timestamp",
                "level",
                "log_type",
                "module",
                "method",
                "message",
                "user",
                "duration",
                "exception_type",
                "is_resolved",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for log in logs:
                writer.writerow(
                    {
                        "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "level": log.get_level_display(),
                        "log_type": log.get_log_type_display(),
                        "module": log.module,
                        "method": log.method,
                        "message": log.message,
                        "user": str(log.user) if log.user else "",
                        "duration": log.duration or "",
                        "exception_type": log.exception_type or "",
                        "is_resolved": "بله" if log.is_resolved else "خیر",
                    }
                )

        self.stdout.write(
            self.style.SUCCESS(f"✅ {logs.count()} لاگ به فایل {filename} صادر شد.")
        )

    def show_help(self):
        """Show usage help"""
        self.stdout.write(self.style.SUCCESS("🔧 راهنمای استفاده از دستور log_manager:"))
        self.stdout.write("")
        self.stdout.write("  📊 نمایش آمار:")
        self.stdout.write("    python manage.py log_manager --stats")
        self.stdout.write("")
        self.stdout.write("  🚨 نمایش لاگ‌های بحرانی:")
        self.stdout.write("    python manage.py log_manager --critical")
        self.stdout.write("")
        self.stdout.write("  ⚠️  نمایش مسائل حل نشده:")
        self.stdout.write("    python manage.py log_manager --unresolved")
        self.stdout.write("")
        self.stdout.write("  🧹 پاکسازی لاگ‌های قدیمی:")
        self.stdout.write("    python manage.py log_manager --cleanup --days 30")
        self.stdout.write("")
        self.stdout.write("  📤 صادرات لاگ‌ها:")
        self.stdout.write("    python manage.py log_manager --export logs.csv")
