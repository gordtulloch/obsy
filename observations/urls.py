# observations/urls.py
from django.conf import settings
from django.urls import path,include
from . import views
from .views import observation_detail_view, observation_all_list
from .views import observation_create,observation_update,observation_delete,ScheduleUpdateView,ScheduleDeleteView, ScheduleRegenView,\
    scheduleMasterList,ScheduleCreateView, daily_observations_task, list_fits_files, fitsfile_detail, sequence_file_list, \
    sequence_file_create, sequence_file_edit, sequence_file_delete,taskPostProcessing,observation_updateDS
from targets.models import Target

urlpatterns = [
    # Observations
    path("",                                observation_all_list.as_view(), name="observation_all_list"),
    path("<uuid:pk>/",                      observation_detail_view.as_view(), name="observation_detail" ),
    path("all_list/",                       observation_all_list.as_view(), name="observation_all_list"),
    path("<uuid:pk>/edit/",                 observation_update, name="observation_update"),
    path("<uuid:pk>/delete/",               observation_delete.as_view(), name="observation_delete"),
    path('create/',                         observation_create, name='observation_create'),
    path('create/<uuid:target_uuid>/',      observation_create, name='observation_create'),
    # Tasks
    path('daily_observations_task/',        daily_observations_task, name='daily_observations_task'),
    path('PostProcess/',                    taskPostProcessing, name='post_processing_task'),
    # Schedules
    path('schedule/',                       scheduleMasterList.as_view(), name='schedule_list'),
    path('schedule/create/',                ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedule/edit/<uuid:pk>/',        ScheduleUpdateView.as_view(), name='schedule_edit'),
    path('schedule/delete/<uuid:pk>/',      ScheduleDeleteView.as_view(), name='schedule_delete'),
    path('schedule/regen/<uuid:pk>/',       ScheduleRegenView.as_view(), name='schedule_regen'),
    # Fits Files
    path('list_fits_files/',                list_fits_files, name='list_fits_files'),
    path('fitsfile/<uuid:pk>/',             fitsfile_detail, name='fits_file_detail'),
    # Sequence Files
    path('sequenceFiles/',                  sequence_file_list, name='sequence_file_list'),
    path('sequenceFiles/create/',           sequence_file_create, name='sequence_file_create'),
    path('sequenceFiles/edit/<uuid:pk>/',   sequence_file_edit, name='sequence_file_edit'),
    path('sequenceFiles/delete/<uuid:pk>/', sequence_file_delete, name='sequence_file_delete'),
]    