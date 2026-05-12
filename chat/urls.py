from django.urls import path

from . import views

urlpatterns = [
    path("", views.chat_page, name="chat-page"),
    path("api/", views.chat_api, name="chat-api-alias"),
    path("api/chat/", views.chat_api, name="chat-api"),
    path("api/chat/clear/", views.clear_chat_history, name="chat-clear"),
]
