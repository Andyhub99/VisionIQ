from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register("inspections", api.InspectionViewSet)
router.register("detections", api.DetectionViewSet)

urlpatterns = [path("stats/", api.stats), path("", include(router.urls))]
