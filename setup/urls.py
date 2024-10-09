# Setup/urls.property
from django.urls import path
from .views import (
    ObservatoryCreateView, ObservatoryUpdateView,
    TelescopeCreateView, TelescopeUpdateView,
    ImagerCreateView, ImagerUpdateView, ObservatoryListView, TelescopeListView, ImagerListView
)

urlpatterns = [
    path('observatory/create/', ObservatoryCreateView.as_view(), name='observatory_create'),
    path('observatory/<int:pk>/edit/', ObservatoryUpdateView.as_view(), name='observatory_update'),
    path('telescope/create/', TelescopeCreateView.as_view(), name='telescope_create'),
    path('telescope/<int:pk>/edit/', TelescopeUpdateView.as_view(), name='telescope_update'),
    path('imager/create/', ImagerCreateView.as_view(), name='imager_create'),
    path('imager/<int:pk>/edit/', ImagerUpdateView.as_view(), name='imager_update'),
    path("observatory_list/", ObservatoryListView.as_view(), name="observatory_list"),
    path("telescope_list/", TelescopeListView.as_view(), name="telescope_list"),
    path("imager_list/", ImagerListView.as_view(), name="imager_list"),
]