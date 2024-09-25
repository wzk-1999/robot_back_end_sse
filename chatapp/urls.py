# chatapp/urls.py
from django.urls import path
from . import views
# from .consumers import ChatConsumer

urlpatterns = [
    path('inquiry/', views.get_recent_messages, name='recent_messages'),
    path('chat/stream/', views.handle_chat_sse, name='chat_stream'),
    # path('api/v1/chat/stream/', ChatConsumer.as_asgi())
    path('chat/stream/sse/', handle_chat_stream_sse),  # SSE GET
]