

SENSOR_RANGES = {
    "ph": {
        "opt_min": 5.5,
        "opt_max": 6.5,
        "scale_min": 0,
        "scale_max": 14,
    },
    "tds": {
        "opt_min": 100,
        "opt_max": 200,
        "scale_min": 0,
        "scale_max": 1000,
    },
    "temp": {
        "opt_min": 18,
        "opt_max": 24,
        "scale_min": 0,
        "scale_max": 40,
    },
    "humidity": {
        "opt_min": 50,
        "opt_max": 70,
        "scale_min": 0,
        "scale_max": 100,
    }
}

EVAL_RANGE = {
    "ph": {
        "good": (5.5, 6.5),
        "ok": (5.0, 7.0),
    },
    "tds": {
        "good": (100, 200),
        "ok": (80, 250),
    },
    "temp": {
        "good": (18, 24),
        "ok": (15, 28),
    },
    "humidity": {
        "good": (50, 70),
        "ok": (40, 80),
    },
}