from django.urls import path
from dashboard import views

urlpatterns = [
    path("hourly_history/", views.hourly_view, name="hourly_page"),
    path("api/hourly_history/", views.hourly_data_api, name="hourly_api"),
    path("current/", views.current_view , name= "current_page"),
    path("api/current/", views.current_data_api , name= "current_api"),
    path("base/", views.base_view,),
    path("", views.home_view),
    
    ]