from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_numeric_range(
    value: float | int, *, field_name: str, minimum: float | int, maximum: float | int
) -> float | int:
    if minimum <= value <= maximum:
        return value
    raise ValueError(f"{field_name} must be between {minimum} and {maximum}.")


class EntryCreate(BaseModel):
    sleep_hours: float
    workout_intensity: str
    supplement_intake: str | None = None
    screen_time: float
    stress_level: int
    date: date

    @field_validator("sleep_hours")
    @classmethod
    def validate_sleep_hours(cls, value: float) -> float:
        if 0 <= value <= 24:
            return value
        raise ValueError("sleep_hours must be between 0 and 24 hours.")

    @field_validator("workout_intensity")
    @classmethod
    def validate_workout_intensity(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("workout_intensity must not be empty.")
        return value

    @field_validator("supplement_intake")
    @classmethod
    def validate_supplement_intake(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("supplement_intake must not be empty when provided.")
        return value

    @field_validator("screen_time")
    @classmethod
    def validate_screen_time(cls, value: float) -> float:
        if 0 <= value <= 24:
            return value
        raise ValueError("screen_time must be between 0 and 24 hours.")

    @field_validator("stress_level")
    @classmethod
    def validate_stress_level(cls, value: int) -> int:
        return int(
            _validate_numeric_range(
                value, field_name="stress_level", minimum=1, maximum=10
            )
        )


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

    sleep_hours: float = Field(...)
    workout_intensity: float = Field(...)
    supplement_intake: float = Field(...)
    screen_time: float = Field(...)
    stress_level: int | None = Field(default=None)

    @field_validator("sleep_hours")
    @classmethod
    def validate_predict_sleep_hours(cls, value: float) -> float:
        if 0 <= value <= 12:
            return value
        raise ValueError("sleep_hours must be between 0 and 12 hours.")

    @field_validator("workout_intensity")
    @classmethod
    def validate_predict_workout_intensity(cls, value: float) -> float:
        return float(
            _validate_numeric_range(
                value, field_name="workout_intensity", minimum=1, maximum=10
            )
        )

    @field_validator("supplement_intake")
    @classmethod
    def validate_predict_supplement_intake(cls, value: float) -> float:
        return float(
            _validate_numeric_range(
                value, field_name="supplement_intake", minimum=0, maximum=10
            )
        )

    @field_validator("screen_time")
    @classmethod
    def validate_predict_screen_time(cls, value: float) -> float:
        if 0 <= value <= 16:
            return value
        raise ValueError("screen_time must be between 0 and 16 hours.")

    @field_validator("stress_level")
    @classmethod
    def validate_predict_stress_level(cls, value: int | None) -> int | None:
        if value is None:
            return value
        if 1 <= value <= 10:
            return value
        raise ValueError("stress_level must be between 1 and 10.")
