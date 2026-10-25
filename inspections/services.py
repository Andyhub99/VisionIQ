import cv2
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Count, Avg, Q
from . import detector
from .models import Inspection, Detection


def validate_upload(f):
    if f.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise ValidationError(f"Image larger than {settings.MAX_UPLOAD_MB} MB.")
    if getattr(f, "content_type", None) not in settings.ALLOWED_IMAGE_TYPES:
        raise ValidationError("Only JPEG, PNG or BMP images are allowed.")


def run_inspection(uploaded_file):
    """Validate, save, run inference, store annotated image + detections."""
    validate_upload(uploaded_file)
    inspection = Inspection.objects.create(image=uploaded_file)
    annotated, dets, ms, name = detector.detect(inspection.image.path)
    ok, buf = cv2.imencode(".jpg", annotated)
    if ok:
        inspection.annotated_image.save(f"ann_{inspection.pk}.jpg", ContentFile(buf.tobytes()), save=False)
    inspection.model_name, inspection.inference_ms = name, round(ms, 1)
    inspection.save()
    Detection.objects.bulk_create([Detection(inspection=inspection, **d) for d in dets])
    return inspection


def class_stats():
    """Per-class analytics used by dashboard, API and CSV export."""
    rows = (Detection.objects.values("label")
            .annotate(total=Count("id"), avg_conf=Avg("confidence"),
                      correct=Count("id", filter=Q(review="correct")),
                      false_pos=Count("id", filter=Q(review="false_positive")))
            .order_by("-total"))
    out = []
    for r in rows:
        reviewed = r["correct"] + r["false_pos"]
        r["precision_reviewed"] = round(r["correct"] / reviewed, 3) if reviewed else None
        r["avg_conf"] = round(r["avg_conf"], 3)
        out.append(r)
    return out
