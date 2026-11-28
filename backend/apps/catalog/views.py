from django.db.models import Count, Q
from django.http import Http404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.progress.models import QuestionProgress

from . import selectors
from .models import Category, Pattern
from .serializers import (
    CategorySerializer,
    PatternSerializer,
    QuestionDetailSerializer,
    QuestionFilterSerializer,
    QuestionSummarySerializer,
    TopicSerializer,
)


class CategoryListView(APIView):
    """GET /categories/ — the three preparation categories with my progress."""

    def get(self, request):
        categories = selectors.categories_with_progress(request.user)
        return Response(CategorySerializer(categories, many=True).data)


class TopicListView(APIView):
    """GET /topics/?category=coding — topics (with section) and my progress per topic."""

    def get(self, request):
        category = request.query_params.get("category") or None
        topics = selectors.topics_with_progress(request.user, category=category)
        return Response(TopicSerializer(topics, many=True).data)


class PatternListView(ListAPIView):
    """GET /patterns/ — coding patterns, for filters."""

    serializer_class = PatternSerializer
    pagination_class = None
    queryset = Pattern.objects.all()


class QuestionListView(ListAPIView):
    """
    GET /questions/?category=&topic=&difficulty=&status=&pattern=&search=&page=

    Paginated. `status` is one of not_started / attempted / completed and is
    evaluated against the requesting user's progress only.
    """

    serializer_class = QuestionSummarySerializer

    def get_queryset(self):
        filters = QuestionFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        return selectors.question_list(self.request.user, **filters.validated_data)


class QuestionDetailView(APIView):
    """GET /questions/{slug}/ — full question plus my progress on it."""

    def get(self, request, slug):
        question = selectors.question_detail(slug)
        if question is None:
            raise Http404
        progress = QuestionProgress.objects.filter(user=request.user, question=question).first()
        serializer = QuestionDetailSerializer(
            question,
            context={
                "request": request,
                "progress": progress,
                "navigation": selectors.question_navigation(question),
                "preferred_language": request.user.profile.preferred_language,
            },
        )
        return Response(serializer.data)


class CatalogStatsView(APIView):
    """
    GET /catalog/stats/ — public. How many published questions each track has
    (the landing page draws one point per question). Aggregate counts only:
    no user data, no question content.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        rows = Category.objects.annotate(
            n=Count("topics__questions", filter=Q(topics__questions__is_published=True))
        ).order_by("order", "name")
        tracks = [{"slug": c.slug, "name": c.name, "count": c.n} for c in rows]
        return Response({"total": sum(t["count"] for t in tracks), "tracks": tracks})
