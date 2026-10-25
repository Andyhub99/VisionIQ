"""Controlled robustness experiment: how much does test mAP drop under blur, noise, brightness shifts?

    !python robustness.py --weights runs/visioniq/weights/best.pt --data /content/neudet_yolo/data.yaml
Writes robustness.json and robustness.csv.
"""
import argparse, csv, json, shutil, tempfile
from pathlib import Path
import cv2, numpy as np, yaml
from ultralytics import YOLO

rng = np.random.default_rng(42)
PERTURBATIONS = {
    "clean": lambda im: im,
    "blur_k5": lambda im: cv2.GaussianBlur(im, (5, 5), 0),
    "blur_k9": lambda im: cv2.GaussianBlur(im, (9, 9), 0),
    "noise_sd15": lambda im: np.clip(im + rng.normal(0, 15, im.shape), 0, 255).astype(np.uint8),
    "noise_sd35": lambda im: np.clip(im + rng.normal(0, 35, im.shape), 0, 255).astype(np.uint8),
    "darker_-60": lambda im: np.clip(im.astype(int) - 60, 0, 255).astype(np.uint8),
    "brighter_+60": lambda im: np.clip(im.astype(int) + 60, 0, 255).astype(np.uint8),
}

ap = argparse.ArgumentParser()
ap.add_argument("--weights", required=True); ap.add_argument("--data", required=True)
a = ap.parse_args()
cfg = yaml.safe_load(open(a.data)); root = Path(cfg["path"])
model = YOLO(a.weights); results = {}

for name, fn in PERTURBATIONS.items():
    tmp = Path(tempfile.mkdtemp())
    (tmp / "images/test").mkdir(parents=True); (tmp / "labels/test").mkdir(parents=True)
    for img in (root / "images/test").iterdir():
        cv2.imwrite(str(tmp / "images/test" / img.name), fn(cv2.imread(str(img))))
    for lbl in (root / "labels/test").iterdir():
        shutil.copy(lbl, tmp / "labels/test" / lbl.name)
    yml = tmp / "d.yaml"
    yml.write_text(yaml.dump({"path": str(tmp), "train": "images/test", "val": "images/test",
                              "test": "images/test", "names": cfg["names"]}))
    m = model.val(data=str(yml), split="test", imgsz=200, verbose=False)
    results[name] = {"mAP50": float(m.box.map50), "recall": float(m.box.mr), "precision": float(m.box.mp)}
    print(name, results[name])

base = results["clean"]["mAP50"]
for r in results.values():
    r["mAP50_drop_vs_clean"] = round(base - r["mAP50"], 4)
json.dump(results, open("robustness.json", "w"), indent=2)
with open("robustness.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["condition", "mAP50", "precision", "recall", "mAP50_drop"])
    for k, v in results.items():
        w.writerow([k, v["mAP50"], v["precision"], v["recall"], v["mAP50_drop_vs_clean"]])
