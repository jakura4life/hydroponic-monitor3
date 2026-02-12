from django.shortcuts import render
from django.http import JsonResponse
from .firebase_service import get_latest_reading, get_history_reading

def latest_sensor_data(request):
    data = get_latest_reading()
    print(type(data), data)
    return JsonResponse(data)

def history_sesnor_data(request):
    data = get_history_reading()
    print(type(data), data)
    return JsonResponse(data)

# Create your views here.
