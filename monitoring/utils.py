"""
Easy-to-use logging utilities for the entire project
"""
import functools
import time
from django.http import HttpRequest
from monitoring.models import CodeLog


class Logger:
    """
    Simplified logging interface for easy use throughout the project
    """

    @staticmethod
    def debug(message, module=None, method=None, **kwargs):
        """Log debug information"""
        return CodeLog.log_debug(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            **kwargs,
        )

    @staticmethod
    def info(message, module=None, method=None, **kwargs):
        """Log general information"""
        return CodeLog.log_info(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            **kwargs,
        )

    @staticmethod
    def warning(message, module=None, method=None, **kwargs):
        """Log warning messages"""
        return CodeLog.log_warning(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            **kwargs,
        )

    @staticmethod
    def error(message, exception=None, module=None, method=None, **kwargs):
        """Log error messages"""
        return CodeLog.log_error(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            exception=exception,
            **kwargs,
        )

    @staticmethod
    def critical(message, exception=None, module=None, method=None, **kwargs):
        """Log critical errors"""
        return CodeLog.log_critical(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            exception=exception,
            **kwargs,
        )

    @staticmethod
    def exception(message, exception, module=None, method=None, **kwargs):
        """Log exceptions with full traceback"""
        return CodeLog.log_exception(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            exception=exception,
            **kwargs,
        )

    @staticmethod
    def user_action(message, user, module=None, method=None, **kwargs):
        """Log user actions for audit trail"""
        return CodeLog.log_user_action(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            user=user,
            **kwargs,
        )

    @staticmethod
    def api_call(message, module=None, method=None, **kwargs):
        """Log API calls"""
        return CodeLog.log_api_call(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            **kwargs,
        )

    @staticmethod
    def security(message, module=None, method=None, **kwargs):
        """Log security events"""
        return CodeLog.log_security_event(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            **kwargs,
        )

    @staticmethod
    def performance(message, duration, module=None, method=None, **kwargs):
        """Log performance metrics"""
        return CodeLog.log_performance(
            module=module or Logger._get_caller_module(),
            method=method or Logger._get_caller_method(),
            message=message,
            duration=duration,
            **kwargs,
        )

    @staticmethod
    def _get_caller_module():
        """Get the module name of the caller"""
        import inspect

        frame = inspect.currentframe()
        try:
            # Go up the stack to find the actual caller
            caller_frame = frame.f_back.f_back
            return caller_frame.f_globals.get("__name__", "unknown")
        finally:
            del frame

    @staticmethod
    def _get_caller_method():
        """Get the method name of the caller"""
        import inspect

        frame = inspect.currentframe()
        try:
            # Go up the stack to find the actual caller
            caller_frame = frame.f_back.f_back
            return caller_frame.f_code.co_name
        finally:
            del frame


def log_exceptions(func=None, *, logger=None, level="ERROR", reraise=True):
    """
    Decorator to automatically log exceptions from functions/methods

    Usage:
        @log_exceptions
        def my_function():
            # This will automatically log any exceptions
            pass

        @log_exceptions(level='CRITICAL', reraise=False)
        def critical_function():
            # This will log as critical and not reraise
            pass
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return f(*args, **kwargs)
            except Exception as e:
                duration = time.time() - start_time

                # Extract request from args if available
                request = None
                user = None
                for arg in args:
                    if isinstance(arg, HttpRequest):
                        request = arg
                        if hasattr(request, "user") and request.user.is_authenticated:
                            user = request.user
                        break

                # Log the exception
                if level == "CRITICAL":
                    Logger.critical(
                        f"استثنا در تابع {f.__name__}: {str(e)}",
                        exception=e,
                        module=f.__module__,
                        method=f.__name__,
                        duration=duration,
                        request=request,
                        user=user,
                        context={
                            "args_count": len(args),
                            "kwargs_keys": list(kwargs.keys()),
                        },
                    )
                else:
                    Logger.exception(
                        f"استثنا در تابع {f.__name__}: {str(e)}",
                        exception=e,
                        module=f.__module__,
                        method=f.__name__,
                        duration=duration,
                        request=request,
                        user=user,
                        context={
                            "args_count": len(args),
                            "kwargs_keys": list(kwargs.keys()),
                        },
                    )

                if reraise:
                    raise
                return None

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def log_performance(threshold=1.0):
    """
    Decorator to log slow-performing functions

    Usage:
        @log_performance(threshold=2.0)  # Log if takes > 2 seconds
        def slow_function():
            pass
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                if duration > threshold:
                    # Extract request from args if available
                    request = None
                    for arg in args:
                        if isinstance(arg, HttpRequest):
                            request = arg
                            break

                    Logger.performance(
                        f"تابع کند: {func.__name__} - {duration:.2f} ثانیه",
                        duration=duration,
                        module=func.__module__,
                        method=func.__name__,
                        request=request,
                        context={"threshold": threshold, "actual_time": duration},
                    )

                return result
            except Exception as e:
                duration = time.time() - start_time
                Logger.exception(
                    f"استثنا در تابع {func.__name__} پس از {duration:.2f} ثانیه",
                    exception=e,
                    module=func.__module__,
                    method=func.__name__,
                    duration=duration,
                )
                raise

        return wrapper

    return decorator


def log_user_action(action_name=None):
    """
    Decorator to log user actions

    Usage:
        @log_user_action("ثبت‌نام در جشنواره")
        def register_user(request):
            pass
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract request and user from args
            request = None
            user = None

            for arg in args:
                if isinstance(arg, HttpRequest):
                    request = arg
                    if hasattr(request, "user") and request.user.is_authenticated:
                        user = request.user
                    break

            # Execute the function
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Log the successful action
                Logger.user_action(
                    action_name or f"عملیات {func.__name__} انجام شد",
                    user=user,
                    module=func.__module__,
                    method=func.__name__,
                    duration=duration,
                    request=request,
                    context={"success": True},
                )

                return result
            except Exception as e:
                duration = time.time() - start_time

                # Log the failed action
                Logger.user_action(
                    f"خطا در {action_name or func.__name__}: {str(e)}",
                    user=user,
                    module=func.__module__,
                    method=func.__name__,
                    duration=duration,
                    request=request,
                    context={"success": False, "error": str(e)},
                )
                raise

        return wrapper

    return decorator


# Convenience aliases
log = Logger()  # For easy access: from monitoring.utils import log
