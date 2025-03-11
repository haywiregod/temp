from django.urls import path, include
from .views import CandidateViewSet

urlpatterns = [
    path("", CandidateViewSet.as_view({"get": "list"})),
    path("search/", CandidateViewSet.as_view({"get": "search"})),
    path(
        "<int:pk>/",
        CandidateViewSet.as_view(
            {
                "put": "update",
                "delete": "delete",
            }
        ),
    ),
]
