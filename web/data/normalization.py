import statistics
from data.models import SensorReading

MAX_PH_JUMP = 0.3
MAX_TDS_JUMP = 100

WINDOW_SIZE = 5
WARMUP_SAMPLES = 3
MAX_REJECTIONS = 3

def median(values):
    return statistics.median(values)

def valid_jump(prev, current, max_delta):
    return abs(current - prev) <= max_delta

def normalize_ph(raw_ph):
    """
    Normalize pH using recent processed values in DB
    with warm-up and recovery to avoid filter lock-in.
    """

    # Hard physical bounds
    # if raw_ph < 0 or raw_ph > 14:
    #     raw_ph = None

    if raw_ph < 0:
        raw_ph = 0

    if raw_ph > 14:
        raw_ph = 14

    recent = list(
        SensorReading.objects
        .filter(ph_clean__isnull=False)
        .order_by("-epoch")
        .values_list("ph_clean", flat=True)[:WINDOW_SIZE]
    )

    # Warm-up phase
    if len(recent) < WARMUP_SAMPLES:
        values = recent + ([raw_ph] if raw_ph is not None else [])
        return round(median(values), 2)

    prev_clean = recent[0]

    # Read rejection counter from DB (simple heuristic)
    rejections = sum(
        abs(v - prev_clean) > MAX_PH_JUMP for v in recent[:MAX_REJECTIONS]
    )

    # Jump rejection
    if raw_ph is not None and abs(raw_ph - prev_clean) > MAX_PH_JUMP:
        if rejections >= MAX_REJECTIONS:
            # Recovery: accept new baseline
            window = [raw_ph]
        else:
            window = recent + [prev_clean]
    else:
        window = recent + ([raw_ph] if raw_ph is not None else [])

    window = window[:WINDOW_SIZE]

    return round(median(window), 2)

def normalize_tds(raw_tds):
    """
    Normalize TDS using recent processed values in DB
    with warm-up and recovery to avoid filter lock-in.
    """

    # Hard physical bounds
    if raw_tds < 0:
        raw_tds = None

    recent = list(
        SensorReading.objects
        .filter(tds_clean__isnull=False)
        .order_by("-epoch")
        .values_list("tds_clean", flat=True)[:WINDOW_SIZE]
    )

    # Warm-up phase
    if len(recent) < WARMUP_SAMPLES:
        values = recent + ([raw_tds] if raw_tds is not None else [])
        return int(median(values))

    prev_clean = recent[0]

    rejections = sum(
        abs(v - prev_clean) > MAX_TDS_JUMP for v in recent[:MAX_REJECTIONS]
    )

    # Jump rejection
    if raw_tds is not None and abs(raw_tds - prev_clean) > MAX_TDS_JUMP:
        if rejections >= MAX_REJECTIONS:
            # Recovery: accept new baseline
            window = [raw_tds]
        else:
            window = recent + [prev_clean]
    else:
        window = recent + ([raw_tds] if raw_tds is not None else [])

    window = window[:WINDOW_SIZE]

    return int(median(window))

