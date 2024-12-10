# Setup/urls.property
from django.urls import path
from .views import (
    ObservatoryCreateView, ObservatoryUpdateView,
    TelescopeCreateView, TelescopeUpdateView,
    ImagerCreateView, ImagerUpdateView, 
    ObservatoryListView, TelescopeListView, ImagerListView, CurrentConfigListView,
    CurrentConfigCreateView, CurrentConfigUpdateView, CurrentConfigDeleteView
)

urlpatterns = [
    path('observatory/create/', ObservatoryCreateView.as_view(), name='observatory_create'),
    path('observatory/<uuid:pk>/edit/', ObservatoryUpdateView.as_view(), name='observatory_update'),
    path('telescope/create/', TelescopeCreateView.as_view(), name='telescope_create'),
    path('telescope/<uuid:pk>/edit/', TelescopeUpdateView.as_view(), name='telescope_update'),
    path('imager/create/', ImagerCreateView.as_view(), name='imager_create'),
    path('imager/<uuid:pk>/edit/', ImagerUpdateView.as_view(), name='imager_update'),
    path("observatory_list/", ObservatoryListView.as_view(), name="observatory_list"),
    path("telescope_list/", TelescopeListView.as_view(), name="telescope_list"),
    path("imager_list/", ImagerListView.as_view(), name="imager_list"),
    path("observatory/<uuid:pk>", ObservatoryUpdateView.as_view(), name="observatory_detail" ),
    path("telescope/<uuid:pk>", TelescopeUpdateView.as_view(), name="telescope_detail" ),
    path("imager/<uuid:pk>", ImagerUpdateView.as_view(), name="imager_detail" ),
    path('currentConfig_list/', CurrentConfigListView.as_view(), name='currentConfig_list'),
    path('currentConfig/create/', CurrentConfigCreateView.as_view(), name='currentConfig_create'),
    path('currentConfig/update/<uuid:pk>/', CurrentConfigUpdateView.as_view(), name='currentConfig_update'),
    path('currentConfig/delete/<uuid:pk>/', CurrentConfigDeleteView.as_view(), name='currentConfig_delete'),

]