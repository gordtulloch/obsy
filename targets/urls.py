# targets/urls.py
from django.urls import path,include
from . import views
from .views import target_all_list,target_query,target_detail_view, schedule

urlpatterns = [
    path("", target_all_list.as_view(), name="target_all_list"),
    path("<uuid:pk>/", target_detail_view.as_view(), name="target_detail" ),
    path("all_list/", target_all_list.as_view(), name="target_all_list"),
    path("<uuid:pk>/edit/", views.target_update.as_view(), name="target_update"),
    path("<uuid:pk>/delete/", views.target_delete.as_view(), name="target_delete"),
    path("create/", views.target_query, name="target_search"),
    path("schedule/", views.schedule, name="schedule_query"),
    path("schedule_edit/", views.schedule_edit.as_view(), name="schedule_edit"),
    path("sequence_upload/", views.sequence_file_upload, name="sequence_file_upload"),
    path("schedule_upload/", views.schedule_file_upload, name="schedule_file_upload"),
    path("sequence_view/", views.sequence_file_list.as_view(), name="sequence_file_list"),
    path("schedule_view/", views.schedule_file_list.as_view(), name="schedule_file_list"),
]
