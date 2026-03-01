from pydantic import BaseModel, Field
from django.db import models
from datetime import datetime,timezone
from django.conf import settings
from typing import ClassVar

class SensorReading(BaseModel):
    epoch: int
    datetime: datetime
    ph: float = Field(ge=0, le=14)
    tds: float | None = None
    airTemp: float | None = None
    humidity: float | None = None

    # --- Factory Methods ---
    @classmethod
    def from_current(cls, data: dict):
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
        # # if isinstance(hour_or_epoch, int):
        # #     dt = datetime.fromtimestamp(hour_or_epoch, tz=timezone.utc)
        # # elif isinstance(hour_or_epoch, datetime):
        # #     # ensure UTC
        # #     dt = hour_or_epoch.astimezone(timezone.utc)
        # # else:
        # #     raise TypeError(f"Invalid type for hour_or_epoch: {type(hour_or_epoch)}")
        # dt = hour
        return cls(
            hour=hour,
            avg_ph=avg_ph,
            avg_tds=avg_tds,
            avg_temp=avg_temp,
            avg_humidity=avg_humidity
        )

    
class Alert(models.Model):
    '''
    Alerts created by django backend.
    1. When created, marks the currend start time and mark as active
    2. Once resolved, is_active is false. The next time the sensor goes opt range, create new alert
    '''
    SENSOR_CHOICES = [
        ("ph", "pH"),
        ("tds", "TDS"),
        ("temp", "Temperature"),
        ("humidity", "Humidity"),
    ]

    sensor = models.CharField(max_length=20, choices=SENSOR_CHOICES)
    severity = models.CharField(max_length=10)  # e.g., "ok", "bad"
    value = models.FloatField()
    message = models.TextField()
    recommendation = models.TextField(null=True,default=None)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notified_critical = models.BooleanField(default=False)

    class Meta:
        db_table = 'alert'

class AlertNotification(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    channel = models.CharField(max_length=20, default="whatsapp")
    status = models.CharField(max_length=20, default=None)

    class Meta:
        db_table ='alert_notifications'