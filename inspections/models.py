from django.db import models


class Inspection(models.Model):
    image = models.ImageField(upload_to="uploads/")
    annotated_image = models.ImageField(upload_to="annotated/", blank=True, null=True)
    model_name = models.CharField(max_length=120, blank=True)
    inference_ms = models.FloatField(default=0)
    missed_count = models.PositiveIntegerField(
        default=0, help_text="Defects the model missed (entered during review)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Inspection #{self.pk}"


class Detection(models.Model):
    class Review(models.TextChoices):
        UNREVIEWED = "unreviewed", "Unreviewed"
        CORRECT = "correct", "Correct"
        FALSE_POSITIVE = "false_positive", "False positive"

    inspection = models.ForeignKey(Inspection, related_name="detections", on_delete=models.CASCADE)
    label = models.CharField(max_length=80)
    confidence = models.FloatField()
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
    review = models.CharField(max_length=20, choices=Review.choices, default=Review.UNREVIEWED)

    class Meta:
        ordering = ["-confidence"]

    def __str__(self):
        return f"{self.label} ({self.confidence:.2f})"
