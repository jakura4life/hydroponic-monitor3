from django.urls import path
from .views import (
    hourly_ph_view,
    arduino_history_data,
    latest_redis_cache,
    )

urlpatterns = [
    path("hourly_history/", hourly_ph_view),
    path("arduino_history/", arduino_history_data),
    path("latest_redis_cache/", latest_redis_cache),
    ]