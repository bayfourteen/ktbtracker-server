from django.urls import path

from .views import CandidatesListView

app_name = "candidates"

urlpatterns = [
    # - - - Home Page - - -
    path("", CandidatesListView.as_view(), name="index"),
]
