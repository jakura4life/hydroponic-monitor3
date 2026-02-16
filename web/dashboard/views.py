from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from sensor.services.hourly_service import get_hourly_data
from sensor.services.listen_service import get_latest_reading

def hourly_view(request):
    hourly_data = get_hourly_data(ignore_cache=False)
    return JsonResponse([h.model_dump() for h in hourly_data], safe=False)



def current_view(request):
    return render(request, "dashboard/current.html")

def current_data_api(request):
    reading = get_latest_reading()

    if not reading:
        return JsonResponse({"error": "No data yet"}, status=404)

    return JsonResponse({
        "ph": reading.ph,
        "tds": reading.tds,
        "airTemp": reading.airTemp,
        "humidity": reading.humidity,
        "timestamp": reading.datetime.isoformat(),
    })