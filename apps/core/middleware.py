"""Security middleware for the application."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from django.conf import settings

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


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

    def __init__(self, get_response: Callable[["HttpRequest"], "HttpResponse"]) -> None:
        """Initialise the middleware and cache the CSP policy string.

        The policy is read once at startup from
        ``settings.CONTENT_SECURITY_POLICY`` and stored on the instance so
        that ``settings`` is not accessed on every request.

        Args:
            get_response: The next middleware or view in the Django chain.
        """
        self.get_response = get_response
        # Cache at startup — avoids a settings lookup on every request.
        self._policy: str | None = getattr(settings, "CONTENT_SECURITY_POLICY", None)

    def __call__(self, request: "HttpRequest") -> "HttpResponse":
        """Process the request and inject the CSP header into the response.

        Args:
            request: The current ``HttpRequest``.

        Returns:
            The ``HttpResponse`` returned by the next middleware or view,
            with the ``Content-Security-Policy`` header added when a policy
            string is configured.
        """
        response = self.get_response(request)
        if self._policy:
            response["Content-Security-Policy"] = self._policy
        return response
