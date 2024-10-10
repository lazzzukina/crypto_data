from django.urls import path

from apps.consumers import CryptoWebSocketConsumer

websocket_urlpatterns = [
    path('ws/crypto/', CryptoWebSocketConsumer.as_asgi()),
]
