from data.redis.redis_cache import (
    cache_latest,
    get_data,
    is_duplicate,
    set_last_epoch,
    # set_last_history_epoch,
)
from data.data_processing.process import normalize_ph
from data.data_processing.process import did_ph_exceed_scale
from services.firebase.firebase_service import (
    store_clean_history,
    compare_last_stored,
    get_latest_clean_history_epoch_from_firebase
)



def current_stream_handler(message):
    """
    Handles updates to sensorData/current
    """
    event = message.event_type
    data = message.data

    if event != "put" or data is None:
        return

    try:
        current_epoch = int(data["epoch"])
        raw_ph = float(data["pH"])
        # raw_tds = float(data["TDS"])
        # temperature = float(data["temperature"])
        # humidity = float(data["humidity"])
    except (KeyError, ValueError, TypeError):
        return
    
    # check if event has been processed.
    if is_duplicate(current_epoch):
        return
    set_last_epoch(current_epoch)
    
    # validate ph value
    if did_ph_exceed_scale(raw_ph):
        return

    # normlaizate values
    ph_clean = normalize_ph(raw_ph)
        
    # cache 
    cache_latest(current_epoch, {
        "ph": ph_clean,
        "tds": data["TDS"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
    })

    if compare_last_stored(current_epoch):
        store_clean_history(current_epoch, {
            "ph": ph_clean,
            "tds": data["TDS"],
            "temperature": data["temperature"],
            "humidity": data["humidity"],
        })
        # set_last_history_epoch(epoch)

    print(f"[CURRENT] epoch={current_epoch} data={data}")

    cache_data = get_data()
    if cache_data:
        print(f"[CLEANED] epoch={current_epoch} cache_data ={cache_data}\n")

