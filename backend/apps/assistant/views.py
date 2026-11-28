import json

from django.db.models import OuterRef, Subquery
from django.http import Http404, StreamingHttpResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.selectors import published_questions

from . import context, services
from .llm import get_provider
from .models import Conversation, Message
from .serializers import (
    ConversationCreateSerializer,
    ConversationDetailSerializer,
    ConversationFilterSerializer,
    ConversationSerializer,
    SendMessageSerializer,
)


def _my_conversations(user):
    """Only ever the requesting user's conversations (others → 404)."""
    return Conversation.objects.filter(user=user).select_related("question__topic__category")


def _get_conversation(user, pk) -> Conversation:
    conv = _my_conversations(user).filter(pk=pk).first()
    if conv is None:
        raise Http404
    return conv


class AssistantStatusView(APIView):
    """GET /assistant/status/ — which provider answers (the UI flags offline demo mode)."""

    def get(self, request):
        provider = get_provider()
        return Response(
            {
                "provider": provider.name,
                "model": provider.model,
                "offline": provider.name == "fake",
                "configured": provider.configured,
            }
        )


class ConversationListView(ListAPIView):
    """
    GET  /assistant/conversations/?question=<slug>  — my conversations, newest first
    POST /assistant/conversations/ {question_slug?, title?}  — start one (optionally about a question)
    """

    serializer_class = ConversationSerializer

    def get_queryset(self):
        filters = ConversationFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        qs = _my_conversations(self.request.user)
        if slug := filters.validated_data.get("question"):
            qs = qs.filter(question__slug=slug)
        return qs

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)
        # Attach each conversation's latest message in one extra query.
        ids = [c.pk for c in page]
        latest = Message.objects.filter(conversation=OuterRef("conversation")).order_by("-created_at", "-id").values("id")[:1]
        last_by_conv = {
            m.conversation_id: m
            for m in Message.objects.filter(conversation_id__in=ids, id=Subquery(latest))
        }
        for c in page:
            c._last_message = last_by_conv.get(c.pk)
        return page

    def post(self, request):
        payload = ConversationCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        question = None
        if slug := payload.validated_data.get("question_slug"):
            question = published_questions().filter(slug=slug).first()
            if question is None:
                raise Http404
        conv = services.create_conversation(request.user, question=question, title=payload.validated_data.get("title", ""))
        return Response(_detail(request.user, conv), status=status.HTTP_201_CREATED)


def _detail(user, conv: Conversation) -> dict:
    messages = list(conv.messages.all())
    return ConversationDetailSerializer(
        conv,
        context={"messages": messages, "capabilities": context.capabilities(user, conv.question).as_dict()},
    ).data


class ConversationDetailView(APIView):
    """GET / DELETE /assistant/conversations/{id}/"""

    def get(self, request, pk):
        return Response(_detail(request.user, _get_conversation(request.user, pk)))

    def delete(self, request, pk):
        _get_conversation(request.user, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventStreamRenderer(BaseRenderer):
    """Lets DRF content negotiation accept `Accept: text/event-stream`.

    Successful responses are StreamingHttpResponses (not rendered by DRF);
    this renderer only formats error bodies, as JSON.
    """

    media_type = "text/event-stream"
    format = "sse"
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return json.dumps(data).encode()


def _sse(events):
    for event in events:
        yield f"event: {event['type']}\ndata: {json.dumps(event, default=str)}\n\n"


class MessageCreateView(APIView):
    """
    POST /assistant/conversations/{id}/messages/ {content, mode, hint_level?}

    Validation errors are ordinary JSON 4xx responses. On success the response
    is a Server-Sent Events stream: `start`, many `token`, then `done` or
    `error` (see services.stream_turn).
    """

    renderer_classes = [JSONRenderer, EventStreamRenderer]
    throttle_scope = "assistant"

    def post(self, request, pk):
        conv = _get_conversation(request.user, pk)
        payload = SendMessageSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        events = services.stream_turn(request.user, conv, **payload.validated_data)

        response = StreamingHttpResponse(_sse(events), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"  # tell nginx-style proxies not to buffer
        return response
