from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from weather import (
    LocationNotSupportedError,
    WeatherServiceError,
    fetch_alerts,
    fetch_forecast,
)

app = FastAPI()


class ForecastRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class ForecastPeriod(BaseModel):
    name: str
    temperature: int | float | None
    temperatureUnit: str
    windSpeed: str
    windDirection: str
    shortForecast: str
    detailedForecast: str
    icon: str
    isDaytime: bool | None


class AlertsRequest(BaseModel):
    state: str = Field(min_length=2, max_length=2)

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str) -> str:
        state = value.strip().upper()
        if len(state) != 2 or not state.isalpha():
            raise ValueError("State must be a two-letter US state code.")
        return state


class Alert(BaseModel):
    event: str
    area: str
    severity: str
    headline: str
    description: str
    instructions: str
    effective: str
    expires: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "Weather API running"}


@app.post("/alerts")
async def alerts(req: AlertsRequest) -> dict[str, list[Alert]]:
    try:
        result = await fetch_alerts(req.state)
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"data": result}


@app.post("/forecast")
async def forecast(req: ForecastRequest) -> dict[str, list[ForecastPeriod]]:
    try:
        result = await fetch_forecast(req.latitude, req.longitude)
    except LocationNotSupportedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WeatherServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"data": result}
