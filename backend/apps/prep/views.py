from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assistant.llm import LLMError

from . import selectors, services
from .models import PreparationPlan
from .serializers import ItemCompletionSerializer, PlanCreateSerializer, PlanDetailSerializer, PlanListSerializer


class PlanGenerationFailed(APIException):
    """The AI call failed (e.g. busy, unreachable). `retryable` tells the UI whether to offer Try again."""

    def __init__(self, message: str, *, retryable: bool, status_code: int):
        super().__init__(detail=message, code="plan_generation_failed")
        self.status_code = status_code
        self.retryable = retryable


def _detail(user, pk):
    plan = selectors.plan_detail(user, pk)
    if plan is None:
        raise Http404
    return PlanDetailSerializer(plan).data


class PlanListView(ListAPIView):
    """
    GET  /prep/plans/  — my study plans, newest first (with progress)
    POST /prep/plans/  {role, job_description, company?, candidate_info?, days_available?, hours_per_day?}
                       — research the company's past interviews on the web, then analyse the pasted JD
                         and generate a sectioned plan (two AI calls, ~20–60 s on the free tier)
    """

    serializer_class = PlanListSerializer

    def get_queryset(self):
        return selectors.my_plans(self.request.user)

    def get_throttles(self):
        # Only generation is expensive (one LLM call on a shared free-tier budget).
        self.throttle_scope = "prep_plan" if self.request.method == "POST" else None
        return super().get_throttles()

    def post(self, request):
        payload = PlanCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        services.check_plan_input(payload.validated_data["job_description"])
        try:
            plan = services.generate_plan(request.user, **payload.validated_data)
        except services.PlanRejected as exc:
            return Response(
                {"error": {"code": "plan_rejected", "message": str(exc)}}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except LLMError as exc:
            raise PlanGenerationFailed(
                exc.user_message, retryable=exc.retryable, status_code=503 if exc.retryable else 502
            ) from exc
        return Response(_detail(request.user, plan.pk), status=status.HTTP_201_CREATED)


class PlanDetailView(APIView):
    """GET / DELETE /prep/plans/{id}/"""

    def get(self, request, pk):
        return Response(_detail(request.user, pk))

    def delete(self, request, pk):
        deleted, _ = PreparationPlan.objects.filter(user=request.user, pk=pk).delete()
        if not deleted:
            raise Http404
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlanItemView(APIView):
    """PATCH /prep/plans/{id}/items/{item_id}/ {completed} — tick an item off (or undo)."""

    def patch(self, request, pk, item_pk):
        item = selectors.my_item(request.user, pk, item_pk)
        if item is None:
            raise Http404
        payload = ItemCompletionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        item = services.set_item_completed(item, payload.validated_data["completed"])
        return Response({"id": item.id, "completed": item.completed, "completed_at": item.completed_at})


class PlanItemLessonView(APIView):
    """
    POST /prep/plans/{id}/items/{item_id}/lesson/ — notes + quiz for a lesson item.
    Generated on first request (one AI call), then stored; later requests return it unchanged.
    """

    throttle_scope = "prep_lesson"

    def get_throttles(self):
        # Only generation costs anything; returning a stored lesson isn't throttled.
        item = selectors.my_item(self.request.user, self.kwargs["pk"], self.kwargs["item_pk"])
        self._item = item
        return [] if item is not None and item.lesson else super().get_throttles()

    def post(self, request, pk, item_pk):
        item = getattr(self, "_item", None) or selectors.my_item(request.user, pk, item_pk)
        if item is None or item.mode != item.Mode.LESSON:
            raise Http404
        try:
            lesson = services.generate_lesson(item)
        except LLMError as exc:
            raise PlanGenerationFailed(
                exc.user_message, retryable=exc.retryable, status_code=503 if exc.retryable else 502
            ) from exc
        return Response({"id": item.id, "lesson": lesson})
