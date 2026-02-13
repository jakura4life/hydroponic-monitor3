from ..services.redis.redis_cache import (
    r,
)

ALPHA = 0.3  # EMA smoothing factor
MAX_PH_JUMP = 0.5
# MAX_TDS_JUMP = 150

def normalize_ph(raw_ph):
    # Physical bounds
    if raw_ph < 0 or raw_ph > 14:
        return None

    prev = r.get("sensor:last_ph")

    if prev is None:
        r.set("sensor:last_ph", raw_ph)
        return round(raw_ph, 2)

    prev = float(prev)

    # Jump protection
    if abs(raw_ph - prev) > MAX_PH_JUMP:
        raw_ph = prev

    clean = ALPHA * raw_ph + (1 - ALPHA) * prev

    r.set("sensor:last_ph", clean)

    return round(clean, 2)


def did_ph_exceed_scale(value):
    if value < 0 or value > 14:
        return True
    return False