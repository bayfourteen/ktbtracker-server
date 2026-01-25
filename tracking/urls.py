from django.urls import path

from tracking import views

app_name = "tracking"

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:tracking_date>/edit/", views.editor, name="editor"),
]
