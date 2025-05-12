from django.utils.deprecation import MiddlewareMixin
from sentry_sdk import configure_scope
from django.contrib.auth.models import AnonymousUser

class SentryContextMiddleware(MiddlewareMixin):
    """
    Middleware sederhana untuk menambahkan context ke Sentry
    """
    def process_request(self, request):
        with configure_scope() as scope:
            # Tambahkan info request dasar
            scope.set_tag("http_method", request.method)
            scope.set_tag("endpoint", request.path)
            
            # Cek apakah user bukan AnonymousUser
            if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                # User terautentikasi (bukan AnonymousUser)
                scope.set_user({
                    "id": request.user.id,
                    "name": request.user.name if hasattr(request.user, 'name') else None,
                    "email": request.user.email if hasattr(request.user, 'email') else None,
                })
            else:
                # User tidak terautentikasi (AnonymousUser)
                scope.set_user({
                    "id": None,
                    "ip_address": self._get_client_ip(request),
                    "authenticated": False
                })
    
    def _get_client_ip(self, request):
        """Mendapatkan IP client dari request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip