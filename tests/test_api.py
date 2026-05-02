from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app
from weather import LocationNotSupportedError, WeatherServiceError


class WeatherApiTests(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_check(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "Weather API running"})

    def test_alerts_normalizes_state_and_returns_structured_data(self) -> None:
        alerts = [
            {
                "event": "Flood Warning",
                "area": "Sample County",
                "severity": "Severe",
                "headline": "Flood warning issued",
                "description": "Flooding is expected.",
                "instructions": "Move to higher ground.",
                "effective": "2026-05-02T00:00:00Z",
                "expires": "2026-05-02T06:00:00Z",
            }
        ]

        with patch("api.fetch_alerts", return_value=alerts) as fetch_alerts:
            response = self.client.post("/alerts", json={"state": "tx"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": alerts})
        fetch_alerts.assert_called_once_with("TX")

    def test_alerts_rejects_invalid_state(self) -> None:
        response = self.client.post("/alerts", json={"state": "Texas"})

        self.assertEqual(response.status_code, 422)

    def test_alerts_maps_upstream_failure_to_bad_gateway(self) -> None:
        with patch("api.fetch_alerts", side_effect=WeatherServiceError("NWS unavailable")):
            response = self.client.post("/alerts", json={"state": "TX"})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "NWS unavailable")

    def test_forecast_returns_structured_periods(self) -> None:
        periods = [
            {
                "name": "Tonight",
                "temperature": 56,
                "temperatureUnit": "F",
                "windSpeed": "8 mph",
                "windDirection": "W",
                "shortForecast": "Mostly Clear",
                "detailedForecast": "Mostly clear, with a low around 56.",
                "icon": "https://api.weather.gov/icons/land/night/skc",
                "isDaytime": False,
            }
        ]

        with patch("api.fetch_forecast", return_value=periods) as fetch_forecast:
            response = self.client.post(
                "/forecast",
                json={"latitude": 37.7749, "longitude": -122.4194},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": periods})
        fetch_forecast.assert_called_once_with(37.7749, -122.4194)

    def test_forecast_rejects_out_of_range_coordinates(self) -> None:
        response = self.client.post(
            "/forecast",
            json={"latitude": 100, "longitude": -122.4194},
        )

        self.assertEqual(response.status_code, 422)

    def test_forecast_maps_unsupported_location_to_not_found(self) -> None:
        with patch(
            "api.fetch_forecast",
            side_effect=LocationNotSupportedError("NWS coverage is US-only"),
        ):
            response = self.client.post(
                "/forecast",
                json={"latitude": 1.2921, "longitude": 36.8219},
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "NWS coverage is US-only")
