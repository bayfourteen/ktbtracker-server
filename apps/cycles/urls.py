from django.urls import path

from .views import CyclesListView

app_name = "cycles"

urlpatterns = [
    # - - - Home Page - - -
    path("", CyclesListView.as_view(), name="index"),
]
