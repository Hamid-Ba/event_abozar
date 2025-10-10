"""
Enhanced Logging Middleware for comprehensive monitoring
"""
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import Http404
from monitoring.models import CodeLog


class EnhancedLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log requests, responses, and exceptions
    """

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """Log incoming requests"""
        request._start_time = time.time()

        # Skip logging for certain paths
        skip_paths = [
            "/admin/jsi18n/",
            "/static/",
            "/media/",
            "/favicon.ico",
        ]

        if any(request.path.startswith(path) for path in skip_paths):
            return None

        # Log API calls and important requests
        if request.path.startswith("/api/") or request.path.startswith("/admin/"):
            context = {
                "path": request.path,
                "method": request.method,
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "query_params": dict(request.GET),
            }

            # Add POST data for non-sensitive endpoints
            if request.method == "POST" and not any(
                sensitive in request.path for sensitive in ["login", "password", "auth"]
            ):
                try:
                    if hasattr(request, "body") and request.body:
                        # Try to parse JSON body
                        content_type = request.META.get("CONTENT_TYPE", "")
                        if "application/json" in content_type:
                            context["post_data"] = json.loads(
                                request.body.decode("utf-8")
                            )
                        else:
                            context["post_data"] = dict(request.POST)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    context["post_data"] = "[Binary or invalid data]"

            CodeLog.log_api_call(
                module="middleware",
                method="process_request",
                message=f"درخواست {request.method} به {request.path}",
                context=context,
                request=request,
                tags=f"{request.method},{request.path.split('/')[1] if len(request.path.split('/')) > 1 else 'root'}",
            )

    def process_response(self, request, response):
        """Log responses and performance metrics"""
        if hasattr(request, "_start_time"):
            duration = time.time() - request._start_time

            # Log slow requests (> 2 seconds)
            if duration > 2.0:
                CodeLog.log_performance(
                    module="middleware",
                    method="process_response",
                    message=f"درخواست کند: {request.path} - {duration:.2f} ثانیه",
                    duration=duration,
                    context={
                        "path": request.path,
                        "method": request.method,
                        "status_code": response.status_code,
                        "response_size": len(response.content)
                        if hasattr(response, "content")
                        else 0,
                    },
                    request=request,
                    tags=f"performance,slow_request,{request.method}",
                )

            # Log API responses
            if request.path.startswith("/api/"):
                log_level = "INFO"
                log_type = "API_CALL"

                if response.status_code >= 400:
                    log_level = "WARNING" if response.status_code < 500 else "ERROR"

                CodeLog.log_message(
                    level=log_level,
                    log_type=log_type,
                    module="middleware",
                    method="process_response",
                    message=f"پاسخ API: {request.path} - وضعیت {response.status_code}",
                    duration=duration,
                    context={
                        "status_code": response.status_code,
                        "response_size": len(response.content)
                        if hasattr(response, "content")
                        else 0,
                    },
                    request=request,
                    tags=f"api_response,status_{response.status_code},{request.method}",
                )

        return response

    def process_exception(self, request, exception):
        """Log exceptions automatically"""
        # Skip 404 errors for common missing files
        if isinstance(exception, Http404):
            skip_404_paths = ["/favicon.ico", "/robots.txt", "/apple-touch-icon"]
            if any(path in request.path for path in skip_404_paths):
                return None

        # Determine log level based on exception type
        log_level = "ERROR"
        if isinstance(exception, (Http404,)):
            log_level = "WARNING"
        elif isinstance(exception, (PermissionError, PermissionDenied)):
            log_level = "SECURITY"
        elif isinstance(exception, (ValueError, TypeError, AttributeError)):
            log_level = "CRITICAL"

        # Extract request context
        context = {
            "path": request.path,
            "method": request.method,
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "referer": request.META.get("HTTP_REFERER", ""),
        }

        # Add user info if available
        if hasattr(request, "user") and request.user.is_authenticated:
            context["user_id"] = request.user.id
            context["user_phone"] = request.user.phone

        # Log the exception
        CodeLog.log_exception(
            module=exception.__class__.__module__ or "unknown",
            method=request.resolver_match.func.__name__
            if request.resolver_match
            else "unknown",
            message=f"استثنا در {request.path}: {str(exception)}",
            exception=exception,
            context=context,
            request=request,
            tags=f"exception,{exception.__class__.__name__},{request.method}",
        )

        # Don't suppress the exception, let Django handle it normally
        return None


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log security-related events
    """

    def process_request(self, request):
        """Log potential security issues"""

        # Log suspicious user agents
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
        suspicious_agents = ["bot", "crawler", "scanner", "curl", "wget", "python"]

        if any(
            agent in user_agent for agent in suspicious_agents
        ) and not request.path.startswith("/api/"):
            CodeLog.log_security_event(
                module="middleware",
                method="security_check",
                message=f"User Agent مشکوک: {user_agent[:100]}",
                context={
                    "user_agent": user_agent,
                    "path": request.path,
                    "ip": CodeLog._get_client_ip(request),
                },
                request=request,
                tags="security,suspicious_user_agent",
            )

        # Log requests to admin area
        if request.path.startswith("/admin/") and request.method == "POST":
            CodeLog.log_security_event(
                module="middleware",
                method="admin_access",
                message=f"دسترسی به پنل مدیریت: {request.path}",
                context={
                    "path": request.path,
                    "method": request.method,
                },
                request=request,
                tags="security,admin_access",
            )

        return None


# Import permission denied for the security middleware
try:
    from django.core.exceptions import PermissionDenied
except ImportError:

    class PermissionDenied(Exception):
        pass
