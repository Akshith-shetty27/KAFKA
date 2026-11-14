from django.urls import path

from . import views

urlpatterns = [
    path("assistant/status/", views.AssistantStatusView.as_view(), name="assistant-status"),
    path("assistant/conversations/", views.ConversationListView.as_view(), name="conversation-list"),
    path("assistant/conversations/<int:pk>/", views.ConversationDetailView.as_view(), name="conversation-detail"),
    path("assistant/conversations/<int:pk>/messages/", views.MessageCreateView.as_view(), name="conversation-messages"),
]
