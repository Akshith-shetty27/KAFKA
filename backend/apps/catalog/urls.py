from django.urls import path

from . import views

urlpatterns = [
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("topics/", views.TopicListView.as_view(), name="topic-list"),
    path("patterns/", views.PatternListView.as_view(), name="pattern-list"),
    path("questions/", views.QuestionListView.as_view(), name="question-list"),
    path("questions/<slug:slug>/", views.QuestionDetailView.as_view(), name="question-detail"),
]
