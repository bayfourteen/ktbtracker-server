from django.urls import path

from .views import JournalsListView

app_name = "journals"

urlpatterns = [
    # - - - Home Page - - -
    path("", JournalsListView.as_view(), name="index"),
]
