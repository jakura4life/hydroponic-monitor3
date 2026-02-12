from django.utils import timezone
from services.firebase_service import get_history_reading
from data.models import SensorReading


def ingest_history_reading():
    """
    fetch data from firebase history directory 
    and stores in postgres db 
    """
    created = 0
    skipped = 0

    raw = get_history_reading()

    if not raw:
        return 0,0

    for epoch, data in raw.items():
        obj, was_created = SensorReading.objects.get_or_create(
            epoch=int(epoch),
            defaults={
                "ph_raw": data["pH"],
                "tds_raw": data["TDS"],
                "temperature": data["temperature"],
                "humidity": data["humidity"],
            }
        )

        if was_created:
            created += 1
        else:
            skipped += 1

    return created, skipped

