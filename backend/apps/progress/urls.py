from django.urls import path

from . import views

urlpatterns = [
    path("questions/<slug:slug>/attempt/", views.QuestionAttemptView.as_view(), name="question-attempt"),
    path("questions/<slug:slug>/answer/", views.QuestionAnswerView.as_view(), name="question-answer"),
    path("questions/<slug:slug>/progress/", views.QuestionProgressView.as_view(), name="question-progress"),
    path("progress/summary/", views.SummaryView.as_view(), name="progress-summary"),
    path("progress/activity/", views.ActivityView.as_view(), name="progress-activity"),
    path("progress/recent/", views.RecentView.as_view(), name="progress-recent"),
    path("progress/plan/", views.PlanView.as_view(), name="progress-plan"),
    path("progress/insights/", views.InsightsView.as_view(), name="progress-insights"),
]
