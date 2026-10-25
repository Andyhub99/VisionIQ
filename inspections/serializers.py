from rest_framework import serializers
from .models import Inspection, Detection


class DetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detection
        fields = ["id", "label", "confidence", "x1", "y1", "x2", "y2", "review"]
        read_only_fields = ["id", "label", "confidence", "x1", "y1", "x2", "y2"]


class InspectionSerializer(serializers.ModelSerializer):
    detections = DetectionSerializer(many=True, read_only=True)

    class Meta:
        model = Inspection
        fields = ["id", "image", "annotated_image", "model_name", "inference_ms",
                  "missed_count", "created_at", "detections"]
        read_only_fields = ["annotated_image", "model_name", "inference_ms", "created_at"]
