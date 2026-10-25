from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("upload/", views.upload, name="upload"),
    path("inspection/<int:pk>/", views.detail, name="detail"),
    path("detection/<int:pk>/review/", views.review, name="review"),
    path("inspection/<int:pk>/missed/", views.set_missed, name="set_missed"),
    path("errors/", views.error_explorer, name="errors"),
    path("export.csv", views.export_csv, name="export_csv"),
]
