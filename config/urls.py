from django.urls import path
from .views import config_view

urlpatterns = [
    path('config/', config_view, name='config_view'),
]