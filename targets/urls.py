# targets/urls.py
from django.urls import path,include
from . import views
from .views import target_list,target_all_list,target_query

urlpatterns = [
    path("", target_list.as_view(), name="target_list"),
    path("all_list/", target_all_list.as_view(), name="target_all_list"),
    path("create/", views.target_query, name="target_search"),
    path("update/<int:pk>/", views.target_update, name="target_update"),
    path("delete/<int:pk>/", views.target_delete, name="target_delete"),
]
