from typing import Any

import httpx

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


class WeatherServiceError(Exception):
    """Raised when the upstream weather service cannot satisfy a request."""


class LocationNotSupportedError(WeatherServiceError):
    """Raised when NWS has no forecast grid for the requested coordinates."""


async def make_nws_request(url: str) -> dict[str, Any]:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise LocationNotSupportedError(
                    "No National Weather Service forecast is available for this location."
                ) from exc
            raise WeatherServiceError("The National Weather Service request failed.") from exc
        except httpx.HTTPError as exc:
            raise WeatherServiceError("Could not connect to the National Weather Service.") from exc


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""


async def fetch_alerts(state: str) -> list[dict[str, str]]:
    """Fetch active weather alerts for a US state as structured data."""
    url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}"
    data = await make_nws_request(url)

    alerts = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        alerts.append(
            {
                "event": props.get("event") or "Unknown",
                "area": props.get("areaDesc") or "Unknown",
                "severity": props.get("severity") or "Unknown",
                "headline": props.get("headline") or "",
                "description": props.get("description") or "No description available",
                "instructions": props.get("instruction") or "",
                "effective": props.get("effective") or "",
                "expires": props.get("expires") or "",
            }
        )

    return alerts


async def fetch_forecast(latitude: float, longitude: float) -> list[dict[str, Any]]:
    """Fetch the next forecast periods for coordinates supported by NWS."""
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    forecast_url = points_data.get("properties", {}).get("forecast")

    if not forecast_url:
        raise LocationNotSupportedError(
            "No National Weather Service forecast is available for this location."
        )

    forecast_data = await make_nws_request(forecast_url)
    periods = forecast_data.get("properties", {}).get("periods", [])

    return [
        {
            "name": period.get("name", "Period"),
            "temperature": period.get("temperature"),
            "temperatureUnit": period.get("temperatureUnit", ""),
            "windSpeed": period.get("windSpeed", ""),
            "windDirection": period.get("windDirection", ""),
            "shortForecast": period.get("shortForecast", ""),
            "detailedForecast": period.get("detailedForecast", ""),
            "icon": period.get("icon", ""),
            "isDaytime": period.get("isDaytime"),
        }
        for period in periods[:5]
    ]


def format_alert_item(alert: dict[str, str]) -> str:
    """Format a structured alert into a readable string."""
    return f"""
Event: {alert["event"]}
Area: {alert["area"]}
Severity: {alert["severity"]}
Description: {alert["description"]}
Instructions: {alert["instructions"] or "No specific instructions provided"}
"""


async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    try:
        alerts = await fetch_alerts(state)
    except WeatherServiceError:
        return "Unable to fetch alerts or no alerts found."

    if not alerts:
        return "No active alerts for this state."

    return "\n---\n".join(format_alert_item(alert) for alert in alerts)


async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    try:
        periods = await fetch_forecast(latitude, longitude)
    except WeatherServiceError:
        return "Unable to fetch forecast data for this location."

    forecasts = []
    for period in periods:
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


def create_mcp_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("weather")
    mcp.tool()(get_alerts)
    mcp.tool()(get_forecast)
    return mcp


def main() -> None:
    mcp = create_mcp_server()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
