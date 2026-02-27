from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from sensor.services.hourly_service import get_hourly_data
from sensor.services.listen_service import get_latest_reading
from django.conf import settings
from sensor.models import Alert



# ------- Web Pages ----------
def home_view(request):
    alerts = Alert.objects.filter(is_active=True)
    context = {
        'active_alerts': alerts,
    }
    return render(request, "dashboard/dashboard.html", context)

def detailed_graph_view(request):
    context = {
        
    }
    return render(request, "dashboard/detailed_graph.html", context)

# ------- api response page -------
def hourly_data_api(request):
    range_label = request.GET.get("range","1d")

    data = get_hourly_data(range_label)
    if not data:
        return JsonResponse({"error": "No data yet"}, status=200)

    payload = [h.model_dump(mode="json") for h in data]

    return JsonResponse(payload, safe=False)

def current_data_api(request):
    return JsonResponse(get_latest_reading())

def sensor_config_api(request):
    return JsonResponse({
        "sensor_ranges": settings.SENSOR_RANGES,
        "valid_timeframes": list(settings.VALID_TIMEFRAME_RANGES)
    })

def active_alerts_api(request):
    #path("api/alerts/", active_alerts_api, name="alerts_api"),
    alerts = Alert.objects.filter(is_active=True).order_by("-created_at")

    data = [
        {
            "sensor": a.sensor,
            "severity": a.severity,
            "message": a.message,
            "value": a.value,
            "created_at": a.created_at,
        }
        for a in alerts
    ]

    return JsonResponse(data, safe=False)

# --- debugging ---

def base_view(request):
    return render(request, 'base.html')