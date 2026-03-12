"""Security middleware for the application."""

from django.conf import settings


class ContentSecurityPolicyMiddleware:
    """Add a ``Content-Security-Policy`` header to every HTTP response.

    The policy string is read from ``settings.CONTENT_SECURITY_POLICY``.
    When the setting is absent or falsy the middleware is a transparent no-op,
    making it safe to define a permissive policy in base.py and override or
    omit it per environment.

    NOTE: The default policy in base.py allows ``unsafe-eval`` because
    TailwindCSS CDN uses ``new Function()`` internally.  For a strict CSP
    without ``unsafe-eval``, replace the CDN with a local Tailwind CLI build
    and tighten the policy accordingly.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._policy = getattr(settings, "CONTENT_SECURITY_POLICY", None)

    def __call__(self, request):
        response = self.get_response(request)
        if self._policy:
            response["Content-Security-Policy"] = self._policy
        return response
