# targets/urls.py
from django.urls import path,include
from . import views
from .views import TargetModel_list,TargetModel_all_list

urlpatterns = [
    path("", TargetModel_list.as_view(), name="TargetModel_list"),
    path("all_list/", TargetModel_all_list.as_view(), name="TargetModel_all_list"),
    path("create/", views.TargetModel_create, name="TargetModel_create"),
    path("update/<int:pk>/", views.TargetModel_update, name="TargetModel_update"),
    path("delete/<int:pk>/", views.TargetModel_delete, name="TargetModel_delete"),
]
