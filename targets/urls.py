# targets/urls.py
from django.urls import path,include
from . import views
from .views import target_list,target_all_list,target_query,target_detail_view

urlpatterns = [
    path("", target_list.as_view(), name="target_all_list"),
    path("<uuid:pk>/", target_detail_view.as_view(), name="target_detail" ),
    path("all_list/", target_all_list.as_view(), name="target_all_list"),
    path("create/", views.target_query, name="target_search"),
    path("<uuid:pk>/edit/", views.target_update.as_view(), name="target_update"),
    path("<uuid:pk>/delete/", views.target_delete.as_view(), name="target_delete"),
]
