# observations/urls.py
from django.conf import settings
from django.urls import path,include
from . import views
from .views import observation_detail_view, observation_all_list

urlpatterns = [
    path("", observation_all_list.as_view(), name="observation_all_list"),
    path("<uuid:pk>/", observation_detail_view.as_view(), name="observation_detail" ),
    path("all_list/", observation_all_list.as_view(), name="observation_all_list"),
    path("<uuid:pk>/edit/", views.observation_update.as_view(), name="observation_update"),
    path("<uuid:pk>/delete/", views.observation_delete.as_view(), name="observation_delete"),
    path("create/", views.observation_create, name="observation_create"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)