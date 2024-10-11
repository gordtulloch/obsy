# Operations/urls.property
from django.urls import path
from .views import (
    CurrentConfigListView,
    CurrentConfigCreateView, 
    CurrentConfigUpdateView, 
    CurrentConfigDeleteView,
    power110PanelView,
    power12PanelView,
)

urlpatterns = [
    path('currentConfig_list/', CurrentConfigListView.as_view(), name='currentConfig_list'),
    path('currentConfig/create/', CurrentConfigCreateView.as_view(), name='currentConfig_create'),
    path('currentConfig/update/<uuid:pk>/', CurrentConfigUpdateView.as_view(), name='currentConfig_update'),
    path('currentConfig/delete/<uuid:pk>/', CurrentConfigDeleteView.as_view(), name='currentConfig_delete'),
    path('power110_panel/', power110PanelView, name='power110_panel'),
    path('power12_panel/', power12PanelView, name='power12_panel'),
]