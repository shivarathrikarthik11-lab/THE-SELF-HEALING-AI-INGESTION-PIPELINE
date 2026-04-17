from fastapi import FastAPI
from pydantic import BaseModel, field_validator
import numpy as np
import logging
from typing import Tuple

# -------------------------------
# Logging Setup
# -------------------------------
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# -------------------------------
# Health Check Endpoint
# -------------------------------
@app.get("/")
def home() -> dict:
    return {"message": "API is running"}


# -------------------------------
# Schema Validation (Pydantic)
# -------------------------------
class Telemetry(BaseModel):
    temperature: float
    humidity: float
    pressure: float

    @field_validator('*')
    def no_nulls(cls, v):
        if v is None:
            raise ValueError("Missing value not allowed")
        return v


# -------------------------------
# Anomaly Detection (Z-score)
# -------------------------------
def z_score(value: float, mean: float, std: float) -> float:
    return abs((value - mean) / std)


# -------------------------------
# Imputation Logic
# -------------------------------
def impute(value: float, mean: float) -> float:
    return mean if value is None else value


# -------------------------------
# Confidence Score
# -------------------------------
def confidence_score(anomalies: int) -> float:
    return max(0.0, 1 - anomalies * 0.3)


# -------------------------------
# Plugin Architecture
# -------------------------------
class ValidationPlugin:
    def validate(self, data: Telemetry) -> Tuple[bool, Telemetry]:
        return True, data


class TemperatureValidator(ValidationPlugin):
    def validate(self, data: Telemetry) -> Tuple[bool, Telemetry]:
        if data.temperature > 100 or data.temperature < -50:
            return False, data
        return True, data


plugins = [TemperatureValidator()]


# -------------------------------
# API Endpoint
# -------------------------------
@app.post("/ingest")
async def ingest(data: Telemetry) -> dict:

    logging.info(f"Received data: {data}")

    anomalies = 0

    # Apply Plugins
    for plugin in plugins:
        valid, data = plugin.validate(data)
        if not valid:
            anomalies += 1

    # Temperature check
    temp_z = z_score(data.temperature, mean=25, std=5)
    if temp_z > 3:
        anomalies += 1
        data.temperature = 25

    # Humidity check
    hum_z = z_score(data.humidity, mean=50, std=10)
    if hum_z > 3:
        anomalies += 1
        data.humidity = 50

    # Pressure check (NEW)
    press_z = z_score(data.pressure, mean=1013, std=20)
    if press_z > 3:
        anomalies += 1
        data.pressure = 1013

    # Confidence score
    score = confidence_score(anomalies)

    if score < 0.7:
        return {
            "status": "REVIEW REQUIRED",
            "confidence_score": score,
            "data": data
        }

    return {
        "status": "ACCEPTED",
        "confidence_score": score,
        "data": data
    }