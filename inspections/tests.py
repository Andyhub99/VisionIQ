import io
from unittest.mock import patch
import numpy as np
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from inspections.models import Inspection, Detection

FAKE = (np.zeros((64, 64, 3), dtype=np.uint8),
        [{"label": "scratches", "confidence": 0.9, "x1": 1, "y1": 2, "x2": 30, "y2": 40}],
        12.5, "fake.pt")


def make_img(ct="image/png", fmt="PNG"):
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), "gray").save(buf, fmt)
    return SimpleUploadedFile("t.png", buf.getvalue(), content_type=ct)


@pytest.fixture(autouse=True)
def tmp_media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.mark.django_db
def test_api_upload_creates_detections(client):
    with patch("inspections.detector.detect", return_value=FAKE):
        r = client.post("/api/inspections/", {"image": make_img()})
    assert r.status_code == 201
    assert r.json()["detections"][0]["label"] == "scratches"
    assert Detection.objects.count() == 1


@pytest.mark.django_db
def test_rejects_wrong_type(client):
    bad = SimpleUploadedFile("x.txt", b"hello", content_type="text/plain")
    r = client.post("/api/inspections/", {"image": bad})
    assert r.status_code == 400


@pytest.mark.django_db
def test_missing_image(client):
    assert client.post("/api/inspections/", {}).status_code == 400


@pytest.mark.django_db
def test_review_flow_and_stats(client):
    with patch("inspections.detector.detect", return_value=FAKE):
        client.post("/api/inspections/", {"image": make_img()})
    d = Detection.objects.get()
    r = client.patch(f"/api/detections/{d.id}/", {"review": "false_positive"}, content_type="application/json")
    assert r.status_code == 200
    stats = client.get("/api/stats/").json()
    assert stats["per_class"][0]["false_pos"] == 1


@pytest.mark.django_db
def test_pages_render(client):
    with patch("inspections.detector.detect", return_value=FAKE):
        client.post(reverse("upload"), {"image": make_img()})
    insp = Inspection.objects.get()
    for url in [reverse("dashboard"), reverse("detail", args=[insp.pk]),
                reverse("errors"), reverse("upload"), reverse("export_csv")]:
        assert client.get(url).status_code == 200
