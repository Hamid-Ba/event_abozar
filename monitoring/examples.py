"""
Enhanced CodeLog System - Usage Examples and Documentation

The enhanced CodeLog system provides comprehensive logging and exception monitoring
for your Django project with Persian admin interface.

🎯 Key Features:
- Automatic exception logging with full traceback
- Performance monitoring 
- User action audit trail
- Request/response logging via middleware
- Security event logging
- Persian admin interface
- Management commands for log analysis
- Easy-to-use decorators and utilities

📋 Usage Examples:
"""

# Example 1: Basic Logging
from monitoring.utils import Logger, log


def example_basic_logging():
    """Basic logging examples"""

    # Simple logging
    Logger.info("عملیات با موفقیت انجام شد")
    Logger.warning("هشدار: حافظه در حال اتمام است")
    Logger.error("خطا در پردازش درخواست")

    # Logging with context
    Logger.info(
        "کاربر جدید ثبت‌نام کرد",
        context={"user_count": 1250, "registration_source": "mobile_app"},
        tags="registration,user_growth",
    )


# Example 2: Exception Logging
from monitoring.utils import log_exceptions


@log_exceptions
def risky_operation():
    """This function will automatically log any exceptions"""
    # Any exception here will be automatically logged
    result = 10 / 0  # This will trigger exception logging
    return result


@log_exceptions(level="CRITICAL", reraise=False)
def critical_operation():
    """Critical operation that shouldn't crash the app"""
    # Exceptions here are logged as CRITICAL and not re-raised
    pass


# Example 3: Performance Monitoring
from monitoring.utils import log_performance


@log_performance(threshold=2.0)  # Log if takes more than 2 seconds
def slow_database_query():
    """This will log if it takes too long"""
    import time

    time.sleep(3)  # Simulate slow operation
    return "data"


# Example 4: User Action Logging
from monitoring.utils import log_user_action


@log_user_action("ثبت‌نام در جشنواره")
def register_user(request):
    """User registration with automatic logging"""
    # User action will be automatically logged
    pass


# Example 5: Manual Exception Logging with Context
def handle_payment():
    """Example of manual exception logging"""
    try:
        # Some payment processing code
        process_payment()
    except PaymentError as e:
        Logger.exception(
            "خطا در پردازش پرداخت",
            exception=e,
            context={
                "payment_amount": 50000,
                "payment_method": "credit_card",
                "user_id": 123,
            },
            tags="payment,error,critical",
        )
        raise


# Example 6: API Logging in Views
from django.http import JsonResponse
from monitoring.utils import Logger


def api_view(request):
    """Example API view with logging"""
    try:
        # Log API call
        Logger.api_call(
            "دریافت لیست کاربران",
            context={"filters": dict(request.GET)},
            request=request,
            tags="api,users,list",
        )

        # Your API logic here
        data = {"users": []}

        return JsonResponse(data)

    except Exception as e:
        Logger.error(
            "خطا در API لیست کاربران",
            exception=e,
            request=request,
            tags="api,error,users",
        )
        return JsonResponse({"error": "خطای داخلی سرور"}, status=500)


# Example 7: Security Event Logging
def login_view(request):
    """Example login view with security logging"""
    username = request.POST.get("username")
    password = request.POST.get("password")

    # Log login attempt
    Logger.security(
        f"تلاش ورود کاربر: {username}",
        context={"username": username, "ip": request.META.get("REMOTE_ADDR")},
        request=request,
        tags="security,login,attempt",
    )

    # Authenticate user...
    if authenticate(username, password):
        Logger.security(
            f"ورود موفق کاربر: {username}",
            request=request,
            tags="security,login,success",
        )
    else:
        Logger.security(
            f"ورود ناموفق کاربر: {username}",
            request=request,
            tags="security,login,failure",
        )


# Example 8: Database Operation Logging
def create_user(user_data):
    """Example database operation with logging"""
    try:
        start_time = time.time()

        # Create user
        user = User.objects.create(**user_data)

        duration = time.time() - start_time

        # Log successful operation
        Logger.database_operation(
            f"کاربر جدید ایجاد شد: {user.phone}",
            context={"user_id": user.id, "phone": user.phone},
            duration=duration,
            tags="database,user,create,success",
        )

        return user

    except Exception as e:
        Logger.error(
            "خطا در ایجاد کاربر",
            exception=e,
            context={"user_data": user_data},
            tags="database,user,create,error",
        )
        raise


# Example 9: Using in Django Views with Class-Based Views
from django.views import View
from monitoring.utils import Logger


class FestivalRegistrationView(View):
    """Example class-based view with logging"""

    def post(self, request):
        """Handle festival registration"""
        try:
            # Log user action
            Logger.user_action(
                "شروع ثبت‌نام در جشنواره",
                user=request.user if request.user.is_authenticated else None,
                request=request,
                context={"form_data": dict(request.POST)},
                tags="festival,registration,start",
            )

            # Process registration...
            registration = self.process_registration(request.POST)

            # Log success
            Logger.user_action(
                "ثبت‌نام در جشنواره با موفقیت انجام شد",
                user=request.user if request.user.is_authenticated else None,
                request=request,
                context={"registration_id": registration.id},
                tags="festival,registration,success",
            )

            return JsonResponse({"success": True, "id": registration.id})

        except Exception as e:
            Logger.error(
                "خطا در ثبت‌نام جشنواره",
                exception=e,
                request=request,
                user=request.user if request.user.is_authenticated else None,
                tags="festival,registration,error",
            )
            return JsonResponse({"error": "خطا در ثبت‌نام"}, status=400)


"""
🔧 Management Commands:

1. Show log statistics:
   python manage.py log_manager --stats

2. Show critical logs:  
   python manage.py log_manager --critical

3. Show unresolved issues:
   python manage.py log_manager --unresolved

4. Clean up old logs:
   python manage.py log_manager --cleanup --days 30

5. Export logs to CSV:
   python manage.py log_manager --export logs.csv

🛡️ Middleware Configuration:

Add to settings.py MIDDLEWARE:
```python
MIDDLEWARE = [
    # ... other middleware
    'monitoring.middleware.EnhancedLoggingMiddleware',
    'monitoring.middleware.SecurityLoggingMiddleware',
    # ... other middleware
]
```

📊 Admin Interface:

The Persian admin interface provides:
- Color-coded log levels
- Advanced filtering and search
- Exception details with traceback
- Performance metrics
- User action audit trail
- Bulk resolution actions

🏷️ Log Types and Levels:

Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL, EXCEPTION, SECURITY, PERFORMANCE
Types: SYSTEM, USER_ACTION, API_CALL, DATABASE, AUTHENTICATION, AUTHORIZATION, 
       VALIDATION, EXCEPTION, PERFORMANCE, SECURITY

💡 Best Practices:

1. Use meaningful messages in Persian
2. Include relevant context data
3. Add appropriate tags for filtering
4. Log user actions for audit trail
5. Monitor performance of critical operations
6. Set up log rotation and cleanup
7. Review unresolved issues regularly
8. Use decorators for automatic logging
"""
