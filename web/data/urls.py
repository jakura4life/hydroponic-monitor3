from django.urls import path
from .views import (
    hourly_ph_view)

urlpatterns = [
    path("hourly_history/", hourly_ph_view)
    ]