from django.urls import path
from .views import RegisterPageView

urlpatterns = [
    path("register/", RegisterPageView.as_view(), name="register"),
    ]