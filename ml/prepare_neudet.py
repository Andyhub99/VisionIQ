"""Convert NEU-DET (Pascal VOC XML) into YOLO format with a reproducible 70/15/15 split.

Usage (Colab):  python prepare_neudet.py --src /content/NEU-DET --out /content/neudet_yolo
It searches --src recursively for .xml files and matching images, so folder layout differences are OK.
"""
import argparse, random, shutil, xml.etree.ElementTree as ET
from pathlib import Path

CLASSES = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]


def convert(xml_path):
    root = ET.parse(xml_path).getroot()
    w = float(root.find("size/width").text); h = float(root.find("size/height").text)
    lines = []
    for obj in root.findall("object"):
        name = obj.find("name").text.strip()
        if name not in CLASSES:
            continue
        b = obj.find("bndbox")
        x1, y1, x2, y2 = (float(b.find(k).text) for k in ("xmin", "ymin", "xmax", "ymax"))
        lines.append(f"{CLASSES.index(name)} {(x1+x2)/2/w:.6f} {(y1+y2)/2/h:.6f} {(x2-x1)/w:.6f} {(y2-y1)/h:.6f}")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    src, out = Path(a.src), Path(a.out)
    images = {p.stem: p for p in src.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}}
    pairs = [(x, images[x.stem]) for x in sorted(src.rglob("*.xml")) if x.stem in images]
    if not pairs:
        raise SystemExit("No xml+image pairs found. Check --src.")
    random.Random(a.seed).shuffle(pairs)
    n = len(pairs); cut1, cut2 = int(n * .70), int(n * .85)
    splits = {"train": pairs[:cut1], "val": pairs[cut1:cut2], "test": pairs[cut2:]}
    for split, items in splits.items():
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)
        for xml_p, img_p in items:
            shutil.copy(img_p, out / "images" / split / img_p.name)
            (out / "labels" / split / f"{img_p.stem}.txt").write_text("\n".join(convert(xml_p)))
    (out / "data.yaml").write_text(
        f"path: {out.resolve()}\ntrain: images/train\nval: images/val\ntest: images/test\n"
        f"names:\n" + "".join(f"  {i}: {c}\n" for i, c in enumerate(CLASSES)))
    print({k: len(v) for k, v in splits.items()}, "->", out / "data.yaml")

if __name__ == "__main__":
    main()
