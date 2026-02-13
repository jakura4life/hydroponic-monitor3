from django.http import JsonResponse
from .models import hourly_ph_model

def hourly_ph_view(request):
    data = hourly_ph_model()
    return JsonResponse(data, safe=False)



# old
from django.shortcuts import render
from django.http import JsonResponse
from services.firebase.firebase_service import get_latest_reading, get_arduino_history_reading
from services.redis.redis_cache import get_data
import json

def latest_sensor_data(request):
    """display firebase db latest directory"""
    data = get_latest_reading()
    print(type(data), data)
    return JsonResponse(data)

def arduino_history_data(request):
    """display firebase db history directory"""
    data = get_arduino_history_reading()
    print(type(data), data)
    return JsonResponse(data)

def latest_redis_cache(request):
    """display redis directory"""
    data = get_data()
    if data:
        return JsonResponse(json.loads(data))
    return JsonResponse({"error": "No data yet"}, status=404)

