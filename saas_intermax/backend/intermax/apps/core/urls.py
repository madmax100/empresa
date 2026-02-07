from django.urls import path

from apps.core import views

urlpatterns = [
    path("health/", views.HealthCheckView.as_view(), name="health"),
    path("roadmap/", views.RoadmapView.as_view(), name="roadmap"),
]
