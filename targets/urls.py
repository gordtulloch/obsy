# targets/urls.py
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path,include
from . import views
from .views import target_all_list,target_query,target_detail_view, schedule, scheduleDetails,targetUpload,targetUploadSuccess,importNGC
from django.conf.urls.static import static
urlpatterns = [
    path("", target_all_list.as_view(), name="target_all_list"),
    path("<uuid:pk>/", target_detail_view.as_view(), name="target_detail" ),
    path("all_list/", target_all_list.as_view(), name="target_all_list"),
    path("<uuid:pk>/edit/", views.target_update.as_view(), name="target_update"),
    path("<uuid:pk>/delete/", views.target_delete.as_view(), name="target_delete"),
    path("create/", views.target_query, name="target_search"),
    path("schedule/", views.schedule.as_view(), name="schedule"), 
    path("schedule/<uuid:pk>/", views.scheduleDetails.as_view(), name="schedule_details"), 
    path("schedule/target/<uuid:pk>/", views.scheduleDetailsItem.as_view(), name="schedule_details_item"), 
    path('import/', targetUpload, name='import'),
    path('importNGC/', importNGC, name='importNGC'),
    path('success/', targetUploadSuccess, name='success'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
