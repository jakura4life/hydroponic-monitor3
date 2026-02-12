from django.db import models


class SensorReading(models.Model):
    epoch = models.BigIntegerField(unique=True) 

    ph_raw = models.FloatField()
    ph_clean = models.FloatField(
        null=True,
        blank=True
        )
    tds_raw = models.IntegerField()
    tds_clean = models.IntegerField(
        null=True,
        blank=True
        )
    temperature = models.FloatField()
    humidity = models.IntegerField()
    
    datetime = models.CharField(50)
    
    class Meta:
        ordering = ["epoch"]
        indexes = [models.Index(fields=["epoch"])]
