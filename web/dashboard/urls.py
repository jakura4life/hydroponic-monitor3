from django.urls import path
from dashboard import views

urlpatterns = [
    # apis
    path("api/hourly_history/", views.hourly_data_api, name="hourly_api"),
    path("api/current/", views.current_data_api , name= "current_api"),
    path("api/config/", views.sensor_config_api, name="config_api"),

    # views
    path("dashboard/", views.home_view, name="dashboard"),
    path("dashboard/detailed_graph/", views.detailed_graph_view, name="detailed_graph"),
    
    # debugging
    path("base/", views.base_view,),
    ]