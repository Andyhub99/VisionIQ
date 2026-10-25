import csv
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Inspection, Detection
from . import services


def dashboard(request):
    stats = services.class_stats()
    ctx = {
        "total_inspections": Inspection.objects.count(),
        "total_detections": Detection.objects.count(),
        "reviewed": Detection.objects.exclude(review="unreviewed").count(),
        "stats": stats,
        "chart_labels": [s["label"] for s in stats],
        "chart_counts": [s["total"] for s in stats],
        "chart_conf": [s["avg_conf"] for s in stats],
        "recent": Inspection.objects.annotate(n=Count("detections"))[:6],
    }
    return render(request, "inspections/dashboard.html", ctx)


def upload(request):
    if request.method == "POST":
        f = request.FILES.get("image")
        if not f:
            messages.error(request, "Please choose an image.")
        else:
            try:
                insp = services.run_inspection(f)
                return redirect("detail", pk=insp.pk)
            except ValidationError as e:
                messages.error(request, " ".join(e.messages))
    return render(request, "inspections/upload.html")


def detail(request, pk):
    insp = get_object_or_404(Inspection.objects.prefetch_related("detections"), pk=pk)
    return render(request, "inspections/detail.html", {"insp": insp})


@require_POST
def review(request, pk):
    det = get_object_or_404(Detection, pk=pk)
    value = request.POST.get("review")
    if value in Detection.Review.values:
        det.review = value
        det.save(update_fields=["review"])
    return redirect("detail", pk=det.inspection_id)


@require_POST
def set_missed(request, pk):
    insp = get_object_or_404(Inspection, pk=pk)
    try:
        insp.missed_count = max(0, int(request.POST.get("missed_count", 0)))
        insp.save(update_fields=["missed_count"])
    except ValueError:
        messages.error(request, "Missed count must be a number.")
    return redirect("detail", pk=pk)


def error_explorer(request):
    qs = Detection.objects.select_related("inspection")
    label = request.GET.get("label", "")
    status_ = request.GET.get("review", "")
    max_conf = request.GET.get("max_conf", "")
    if label:
        qs = qs.filter(label=label)
    if status_:
        qs = qs.filter(review=status_)
    if max_conf:
        try:
            qs = qs.filter(confidence__lte=float(max_conf))
        except ValueError:
            pass
    ctx = {
        "detections": qs.order_by("confidence")[:100],
        "labels": Detection.objects.values_list("label", flat=True).distinct(),
        "review_choices": Detection.Review.choices,
        "sel": {"label": label, "review": status_, "max_conf": max_conf},
        "missed_total": sum(Inspection.objects.values_list("missed_count", flat=True)),
    }
    return render(request, "inspections/errors.html", ctx)


def export_csv(request):
    """Flat table for Power BI / Excel."""
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="visioniq_detections.csv"'
    w = csv.writer(resp)
    w.writerow(["detection_id", "inspection_id", "created_at", "label", "confidence",
                "x1", "y1", "x2", "y2", "review", "model", "inference_ms"])
    for d in Detection.objects.select_related("inspection").iterator():
        i = d.inspection
        w.writerow([d.id, i.id, i.created_at.isoformat(), d.label, round(d.confidence, 4),
                    round(d.x1, 1), round(d.y1, 1), round(d.x2, 1), round(d.y2, 1),
                    d.review, i.model_name, i.inference_ms])
    return resp
