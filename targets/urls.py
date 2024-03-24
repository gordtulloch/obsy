# targets/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.TargetModel_list, name="TargetModel_list"),
    path("create/", views.TargetModel_create, name="TargetModel_create"),
    path("update/<int:pk>/", views.TargetModel_update, name="TargetModel_update"),
    path("delete/<int:pk>/", views.TargetModel_delete, name="TargetModel_delete"),
]
