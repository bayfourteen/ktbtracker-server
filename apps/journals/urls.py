from django.urls import path

from .views import JournalsEditView, JournalsListView

app_name = "journals"

urlpatterns = [
    # - - - Home Page - - -
    path("", JournalsListView.as_view(), name="index"),
    path("<int:pk>/edit/", JournalsEditView.as_view(), name="edit"),
]
