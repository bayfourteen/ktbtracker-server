from django.urls import path

from tracking import views
from tracking.views import TrackingFormView, TrackingListView

app_name = "tracking"

urlpatterns = [
    path("", TrackingListView.as_view(), name="index"),
    path("editor/", TrackingFormView.as_view(), name="editor"),
]
