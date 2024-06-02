# targets/urls.py
from django.urls import path,include
from . import views
from .views import fitsFile_all_list,fitsHeader_all_list,fitsFile_detail_view, fitsFile_detail_view

urlpatterns = [
    path("", fitsFile_all_list.as_view(), name="fitsFile_all_list"),
    path("all_fitsFiles/", fitsHeader_all_list.as_view(), name="fitsHeader_all_list"),
    path("all_fitsHeaders/", fitsHeader_all_list.as_view(), name="fitsHeader_all_list"),
]
