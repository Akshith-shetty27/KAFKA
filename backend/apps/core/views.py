import logging

from django.db import DatabaseError, connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class HealthView(APIView):
    """Liveness + database check. Public, unauthenticated, no data exposed."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except DatabaseError:
            logger.exception("Health check: database unreachable")
            raise ServiceUnavailable("Database unreachable.")
        return Response({"status": "ok", "database": "ok"})
