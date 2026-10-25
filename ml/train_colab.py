"""Fine-tune YOLOv8n and record test metrics. Run on Colab GPU (Runtime > Change runtime type > T4).

    !pip -q install ultralytics
    !python train_colab.py --data /content/neudet_yolo/data.yaml
Outputs: runs/visioniq/weights/best.pt and metrics.json (use these numbers on your CV).
"""
import argparse, json
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--epochs", type=int, default=50)
ap.add_argument("--imgsz", type=int, default=200)  # NEU-DET images are 200x200
a = ap.parse_args()

model = YOLO("yolov8n.pt")
model.train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=32, seed=42,
            project="runs", name="visioniq", exist_ok=True)

best = YOLO("runs/visioniq/weights/best.pt")
m = best.val(data=a.data, split="test", imgsz=a.imgsz)
metrics = {
    "split": "test (held out)",
    "precision": float(m.box.mp), "recall": float(m.box.mr),
    "mAP50": float(m.box.map50), "mAP50-95": float(m.box.map),
    "per_class_mAP50": {m.names[i]: float(v) for i, v in zip(m.box.ap_class_index, m.box.ap50)},
}
json.dump(metrics, open("metrics.json", "w"), indent=2)
print(json.dumps(metrics, indent=2))
