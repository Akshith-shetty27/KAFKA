"""
One error shape for the whole API, so the frontend has a single place to
read errors from:

    {"error": {"code": "validation_error", "message": "...", "fields": {...}}}

`fields` is only present for validation errors and maps field name → list of
messages (DRF's native format).
"""

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    # Convert Django's own exceptions into their DRF equivalents first.
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, context)
    if response is None:
        # Not an API exception: let Django turn it into a 500 (and log it).
        return None

    if isinstance(exc, exceptions.ValidationError):
        detail = exc.detail
        if isinstance(detail, dict):
            fields = detail
            non_field = detail.get("non_field_errors")
            message = str(non_field[0]) if non_field else "Please correct the highlighted fields."
        else:
            fields = None
            message = str(detail[0]) if isinstance(detail, list) and detail else str(detail)
        body = {"code": "validation_error", "message": message}
        if fields:
            body["fields"] = fields
    else:
        detail = getattr(exc, "detail", None)
        code = detail.code if hasattr(detail, "code") else getattr(exc, "default_code", "error")
        body = {"code": code, "message": str(detail) if detail else str(exc)}

    response.data = {"error": body}
    return response


class ServiceUnavailable(exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable."
    default_code = "service_unavailable"
