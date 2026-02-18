from pydantic import BaseModel, Field
from django.db import models
from datetime import datetime,timezone

class SensorReading(BaseModel):
    epoch: int
    datetime: datetime
    ph: float = Field(ge=0, le=14)
    tds: float | None = None
    airTemp: float | None = None
    humidity: float | None = None

    @classmethod
    def from_current(cls, data:dict):
        return cls(
            epoch=data["epoch"],
            datetime=data["datetime"],
            tds=data["TDS"],
            ph=data["pH"],
            humidity=data["humidity"],
            airTemp=data["temperature"],
        )
    
    @classmethod
    def from_history(cls, epoch: int, data: dict):
        return cls(
            epoch=epoch,
            datetime=data["datetime"],
            tds=data["TDS"],
            ph=data["pH"],
            humidity=data["humidity"],
            airTemp=data["temperature"],
        )
    




class HourlyAggregate(BaseModel):
    hour: datetime
    avg_ph: float
    avg_tds: float
    avg_temp: float
    avg_humidity: float

    @classmethod
    def from_epoch(cls, hour, avg_ph, avg_tds, avg_temp, avg_humidity):
        # if isinstance(hour_or_epoch, int):
        #     dt = datetime.fromtimestamp(hour_or_epoch, tz=timezone.utc)
        # elif isinstance(hour_or_epoch, datetime):
        #     # ensure UTC
        #     dt = hour_or_epoch.astimezone(timezone.utc)
        # else:
        #     raise TypeError(f"Invalid type for hour_or_epoch: {type(hour_or_epoch)}")
        dt = hour
        return cls(
            hour=dt,
            avg_ph=avg_ph,
            avg_tds=avg_tds,
            avg_temp=avg_temp,
            avg_humidity=avg_humidity
        )
    
    def generate_feedback(hourly):
        messages = []

        if hourly.avg_ph > 7:
            messages.append("pH high — adjust nutrient solution")

        if hourly.avg_temp > 28:
            messages.append("High temperature risk")

        return messages