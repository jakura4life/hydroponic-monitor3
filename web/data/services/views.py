# from django.shortcuts import render
# from django.http import JsonResponse
# from .firebase.firebase_service import get_latest_reading, get_arduino_history_reading
# from data.redis.redis_cache import get_data
# import json

# def latest_sensor_data(request):
#     """display firebase db latest directory"""
#     data = get_latest_reading()
#     print(type(data), data)
#     return JsonResponse(data)

# def history_sesnor_data(request):
#     """display firebase db history directory"""
#     data = get_arduino_history_reading()
#     print(type(data), data)
#     return JsonResponse(data)


# ## data dir

# def latest_redis(request):
#     """display redis directory"""
#     data = get_data()
#     if data:
#         return JsonResponse(json.loads(data))
#     return JsonResponse({"error": "No data yet"}, status=404)

# # Create your views here.
