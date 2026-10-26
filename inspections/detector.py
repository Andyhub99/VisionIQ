
"""YOLO wrapper. Loads the model lazily so Django starts fast and tests can mock it."""
import time
import tempfile
from pathlib import Path

from django.conf import settings

_model = None
_model_name = ""


def _load():
    global _model, _model_name

    if _model is None:
        from ultralytics import YOLO

        path = Path(settings.BASE_DIR) / settings.MODEL_PATH

        if not path.is_file():
            raise FileNotFoundError(
                f"Trained defect model not found: {path}. "
                "Set MODEL_PATH to the trained model file."
            )

        _model = YOLO(str(path))
        _model_name = path.name

    return _model, _model_name


def detect(image_path):
    """Return (annotated_bgr_array, detections_list, inference_ms, model_name)."""
    model, name = _load()
    source_path = Path(image_path)
    temporary_path = None

    try:
        # YOLO may not recognize .jfif even when the file contains a valid JPEG.
        if source_path.suffix.lower() == ".jfif":
            from PIL import Image

            with Image.open(source_path) as image:
                image = image.convert("RGB")

                with tempfile.NamedTemporaryFile(
                    suffix=".jpg", delete=False
                ) as temporary_file:
                    temporary_path = temporary_file.name

                image.save(temporary_path, format="JPEG")

            image_source = temporary_path
        else:
            image_source = str(source_path)

        start = time.perf_counter()
        result = model.predict(
            image_source,
            conf=settings.CONF_THRESHOLD,
            device="cpu",
            verbose=False,
        )[0]
        ms = (time.perf_counter() - start) * 1000

        detections = []

        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append({
                "label": result.names[int(box.cls[0])],
                "confidence": float(box.conf[0]),
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
            })

        return result.plot(), detections, ms, name

    finally:
        # Remove the temporary JPEG even if inference fails.
        if temporary_path and Path(temporary_path).exists():
            Path(temporary_path).unlink()
