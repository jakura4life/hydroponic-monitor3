from django.urls import path
from .views import latest_sensor_data, history_sesnor_data

urlpatterns = [
    path("latest/", latest_sensor_data),
    path("history/", history_sesnor_data),
]