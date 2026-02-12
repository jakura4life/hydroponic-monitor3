from data.models import SensorReading
from data.normalization import normalize_ph, normalize_tds
from django.db import transaction


def process_unprocessed_readings():
    qs = SensorReading.objects.filter(
        ph_clean__isnull=True,
        tds_clean__isnull=True
    ).order_by("epoch")

    updated = 0

    for r in qs:
        r.ph_clean = normalize_ph(r.ph_raw)
        r.tds_clean = normalize_tds(r.tds_raw)
        r.save(update_fields=["ph_clean", "tds_clean"])
        updated += 1

    return updated

def reset_clean_sensor_values():
    """
    Reset all normalized sensor values.
    Sets ph_clean and tds_clean to NULL.
    """
    with transaction.atomic():
        updated = SensorReading.objects.update(
            ph_clean=None,
            tds_clean=None
        )

    return updated