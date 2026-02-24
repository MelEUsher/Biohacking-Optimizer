from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


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
