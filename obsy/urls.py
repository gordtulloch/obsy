from django.contrib import admin
from django.urls import include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("pages.urls")),
    path("targets/", include("targets.urls")),
    path("observations/", include("observations.urls")),
    path("setup/", include("setup.urls")),
    path("operations/", include("operations.urls")),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

