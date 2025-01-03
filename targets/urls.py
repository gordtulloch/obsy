# targets/urls.py
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path,include
from . import views
from .views import target_all_list,target_query,target_detail_view, upload_targets_view, vs_all_list,create_exoplanet_filter # , ex_all_list
from django.conf.urls.static import static
urlpatterns = [
    path("", target_all_list, name="target_all_list"),
    path("<uuid:pk>/", target_detail_view, name="target_detail" ),
    path("all_list/", target_all_list, name="target_all_list"),
    path("<uuid:pk>/edit/", views.target_update.as_view(), name="target_update"),
    path("<uuid:pk>/delete/", views.target_delete.as_view(), name="target_delete"),
    path("create/", views.target_query, name="target_search"),
    path('upload/', upload_targets_view, name='upload_targets'),
    path('vs/', vs_all_list, name='vs_all_list'),
    #path('ex/', ex_all_list, name='ex_all_list'),
    path('ex_filter/', create_exoplanet_filter, name='create_exoplanet_filter'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
