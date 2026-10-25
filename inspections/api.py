from django.core.exceptions import ValidationError
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Inspection, Detection
from .serializers import InspectionSerializer, DetectionSerializer
from . import services


class InspectionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Inspection.objects.prefetch_related("detections")
    serializer_class = InspectionSerializer

    def create(self, request, *args, **kwargs):
        f = request.FILES.get("image")
        if not f:
            return Response({"image": "This field is required."}, status=400)
        try:
            inspection = services.run_inspection(f)
        except ValidationError as e:
            return Response({"image": e.messages}, status=400)
        return Response(self.get_serializer(inspection).data, status=status.HTTP_201_CREATED)


class DetectionViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """PATCH {"review": "correct" | "false_positive"} to review a detection."""
    queryset = Detection.objects.all()
    serializer_class = DetectionSerializer
    http_method_names = ["get", "patch"]


@api_view(["GET"])
def stats(request):
    return Response({
        "inspections": Inspection.objects.count(),
        "detections": Detection.objects.count(),
        "per_class": services.class_stats(),
    })
