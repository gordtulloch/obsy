# routing.py

from django.urls import path
from .consumers import LogConsumer

websocket_urlpatterns = [
    path('ws/logs/', LogConsumer.as_asgi()),
]