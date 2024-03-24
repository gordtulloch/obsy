from django.contrib import admin
from django.urls import include, path
from . import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("pages.urls")),
    path("targets/", include("targets.urls")),
]
