from django.urls import path

from tracking import views

app_name = "tracking"

urlpatterns = [
    path("", views.index, name="index"),
    path("editor/", views.editor, name="editor"),
]
