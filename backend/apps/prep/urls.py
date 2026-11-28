from django.urls import path

from . import views

urlpatterns = [
    path("prep/plans/", views.PlanListView.as_view(), name="plan-list"),
    path("prep/plans/<int:pk>/", views.PlanDetailView.as_view(), name="plan-detail"),
    path("prep/plans/<int:pk>/items/<int:item_pk>/", views.PlanItemView.as_view(), name="plan-item"),
    path("prep/plans/<int:pk>/items/<int:item_pk>/lesson/", views.PlanItemLessonView.as_view(), name="plan-item-lesson"),
]
