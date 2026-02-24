from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EntryCreate(BaseModel):
    sleep_hours: float
    workout_intensity: str
    supplement_intake: str | None = None
    screen_time: float
    stress_level: int
    date: date


class EntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sleep_hours: float
    workout_intensity: str
    supplement_intake: str | None = None
    screen_time: float
    stress_level: int
    date: date


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sleep_hours: float = Field(..., ge=0.0, le=12.0)
    workout_intensity: float = Field(..., ge=1.0, le=10.0)
    supplement_intake: float = Field(..., ge=0.0, le=10.0)
    screen_time: float = Field(..., ge=0.0, le=16.0)
