from django.urls import reverse
from rest_framework.test import APITestCase


class HealthEndpointTests(APITestCase):
    def test_health_is_public_and_reports_database(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})

    def test_unknown_route_returns_404(self):
        response = self.client.get("/api/v1/does-not-exist/")
        self.assertEqual(response.status_code, 404)
