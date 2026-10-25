# VisionIQ - Surface Defect Inspection Platform

VisionIQ is a Django-based surface defect inspection application that uses YOLO object detection to identify potential defects in steel-surface images. It includes inspection history, human review, analytics, and machine-learning experiment scripts.

## Features

- Upload steel-surface images for defect inspection
- View annotated detection results and confidence scores
- Review and correct predictions
- Explore inspection statistics through a dashboard
- Filter inspection results and export data to CSV
- Access inspection endpoints through a REST API
- Train and evaluate a YOLO model using Google Colab
- Run robustness experiments involving blur, noise, and brightness changes
- Run automated tests with the model mocked for faster testing

## Technology Stack

- Python
- Django and Django REST Framework
- Ultralytics YOLO
- Chart.js
- pytest
- Google Colab for model training

## Project Structure

```text
visioniq/
├── config/
├── inspections/
├── ml/
│   ├── prepare_neudet.py
│   ├── train_colab.py
│   ├── robustness.py
│   └── weights/
├── manage.py
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## Run Locally on Windows

Open PowerShell in the project directory:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

Run automated tests with:

```powershell
pytest
```

If Python 3.13 is not installed, install a compatible Python version before creating the environment.

## Model Training

The scripts in `ml/` support preparing the NEU-DET dataset, training a YOLO model, and evaluating robustness. Training can be performed in Google Colab with a compatible GPU runtime.

Follow the commands and dataset paths documented in the training scripts. Keep datasets and trained weights out of Git unless there is a specific, appropriate reason to distribute them.

The application may use a fallback model when the fine-tuned weights are unavailable. Verify the configured model path and application behavior before relying on inspection results.

## Model Evaluation

VisionIQ uses a fine-tuned YOLOv8n model trained on the NEU-DET steel surface defect dataset.

### Held-out Test Results

The model was evaluated on 270 held-out test images containing 606 annotated defect instances.

| Metric | Result |
|---|---:|
| Precision | 70.98% |
| Recall | 67.16% |
| mAP@50 | 71.94% |
| mAP@50–95 | 41.85% |

### Per-Class mAP@50

| Defect Class | mAP@50 |
|---|---:|
| Crazing | 35.11% |
| Inclusion | 78.93% |
| Patches | 95.09% |
| Pitted Surface | 82.98% |
| Rolled-in Scale | 46.94% |
| Scratches | 92.56% |

### Limitations

Performance varies by defect category. Patches and scratches achieved the strongest results, while crazing and rolled-in scale require further improvement. These results apply to the held-out NEU-DET test split and do not guarantee equivalent performance in real-world industrial environments.

The trained model is stored locally at `ml/weights/best.pt`. Model weights should not be committed to GitHub by default.


## Dataset

The project is designed to work with NEU-DET, a dataset of steel-surface defects. Check the dataset's license and cite the original source when distributing or presenting work based on it.

## Future Improvements

- Add authentication and role-based access
- Improve model evaluation and per-class reporting
- Add deployment-ready configuration and persistent image storage
- Document reproducible experiments and model limitations

## Disclaimer

VisionIQ is a project for learning and experimentation. Its predictions should not be treated as a substitute for validated industrial quality-control procedures.
