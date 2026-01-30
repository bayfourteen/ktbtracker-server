from django.urls import path

from tracking import views
from tracking.views import TrackingFormView

app_name = "tracking"

urlpatterns = [
    path("", views.index, name="index"),
    path("editor/", TrackingFormView.as_view(), name="editor"),
]
