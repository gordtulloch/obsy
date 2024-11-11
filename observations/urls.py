# observations/urls.py
from django.conf import settings
from django.urls import path,include
from . import views
from .views import observation_detail_view, observation_all_list
from .views import observation_create,schedule, scheduleDetails, \
    scheduleDetailsItem,daily_observations_task, list_fits_files, fitsfile_detail
from targets.models import target

urlpatterns = [
    path("", observation_all_list.as_view(), name="observation_all_list"),
    path("<uuid:pk>/", observation_detail_view.as_view(), name="observation_detail" ),
    path("all_list/", observation_all_list.as_view(), name="observation_all_list"),
    path("<uuid:pk>/edit/", views.observation_update.as_view(), name="observation_update"),
    path("<uuid:pk>/delete/", views.observation_delete.as_view(), name="observation_delete"),
    path('create/', observation_create, name='observation_create'),
    path('create/<uuid:target_uuid>/',observation_create, name='observation_create'),
    path("schedule/", views.schedule.as_view(), name="schedule"), 
    path("schedule/<uuid:pk>/", views.scheduleDetails.as_view(), name="schedule_details"), 
    path("schedule/target/<uuid:pk>/", views.scheduleDetailsItem.as_view(), name="schedule_details_item"), 
    path('daily_observations_task/', daily_observations_task, name='daily_observations_task'),
    path('fits-files/', list_fits_files, name='list_fits_files'),
    path('fitsfile/<uuid:pk>/', views.fitsfile_detail, name='fits_file_detail'),
]    