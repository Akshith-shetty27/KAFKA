from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.selectors import published_questions
from apps.catalog.serializers import ProgressStateSerializer

from . import selectors, services
from .serializers import (
    ActivityQuerySerializer,
    AnswerInputSerializer,
    AnswerResultSerializer,
    PlanSerializer,
    ProgressUpdateSerializer,
    RecentProgressSerializer,
    RecentQuerySerializer,
)


def _get_question(slug):
    question = published_questions().filter(slug=slug).first()
    if question is None:
        raise Http404
    return question


class QuestionAttemptView(APIView):
    """POST /questions/{slug}/attempt/ — the user opened/started this question."""

    def post(self, request, slug):
        progress = services.record_attempt(request.user, _get_question(slug))
        return Response(ProgressStateSerializer(progress).data)


class QuestionAnswerView(APIView):
    """POST /questions/{slug}/answer/ {option_id} — grade an MCQ answer server-side."""

    def post(self, request, slug):
        question = _get_question(slug)
        payload = AnswerInputSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        result = services.submit_answer(request.user, question, payload.validated_data["option_id"])
        return Response(AnswerResultSerializer(result).data)


class QuestionProgressView(APIView):
    """
    PUT    /questions/{slug}/progress/ {"status": "completed"} — mark done
    DELETE /questions/{slug}/progress/                       — reset my progress
    """

    def put(self, request, slug):
        question = _get_question(slug)
        payload = ProgressUpdateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        progress = services.mark_completed(request.user, question)
        return Response(ProgressStateSerializer(progress).data)

    def delete(self, request, slug):
        services.reset_progress(request.user, _get_question(slug))
        return Response(status=status.HTTP_204_NO_CONTENT)


class SummaryView(APIView):
    """GET /progress/summary/ — dashboard totals, accuracy, streak, per-category progress."""

    def get(self, request):
        return Response(selectors.summary(request.user))


class ActivityView(APIView):
    """GET /progress/activity/?days=7 — per-day counts in the user's timezone."""

    def get(self, request):
        query = ActivityQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        days = query.validated_data["days"]
        return Response({"days": days, "series": selectors.daily_activity(request.user, days)})


class RecentView(APIView):
    """GET /progress/recent/?limit=10 — questions I touched most recently."""

    def get(self, request):
        query = RecentQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        records = selectors.recent_progress(request.user, query.validated_data["limit"])
        return Response(RecentProgressSerializer(records, many=True).data)


class PlanView(APIView):
    """GET /progress/plan/ — today's plan and recommended topics."""

    def get(self, request):
        return Response(PlanSerializer(selectors.todays_plan(request.user)).data)


class InsightsView(APIView):
    """GET /progress/insights/ — per-topic completion and accuracy, difficulty breakdown, focus areas."""

    def get(self, request):
        return Response(selectors.insights(request.user))
