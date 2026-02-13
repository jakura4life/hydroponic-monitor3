from django.http import JsonResponse
from .models import hourly_ph_model

def hourly_ph_view(request):
    data = hourly_ph_model()
    return JsonResponse(data, safe=False)
