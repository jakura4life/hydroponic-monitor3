from django.urls import path
from dashboard import views

urlpatterns = [
    # apis
    path("api/hourly_history/", views.hourly_data_api, name="hourly_api"),
    path("api/current/", views.current_data_api , name= "current_api"),

    # views
    path("", views.home_view),
    
    # debugging
    path("base/", views.base_view,),
    ]