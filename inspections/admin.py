from django.contrib import admin
from .models import Inspection, Detection

class DetectionInline(admin.TabularInline):
    model = Detection
    extra = 0

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ("id", "model_name", "inference_ms", "created_at")
    inlines = [DetectionInline]

admin.site.register(Detection)
