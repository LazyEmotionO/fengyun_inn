from django import forms
from .models import Pond

# 各物種的參考建議門檻，顯示在表單欄位 help_text
SPECIES_HINTS = {
    "文蛤": {"temp": "20–30", "ph": "7.5–8.5", "do": "≥ 3", "sal": "15–30"},
    "白蝦": {"temp": "23–30", "ph": "7.5–8.5", "do": "≥ 5", "sal": "10–35"},
    "牡蠣": {"temp": "15–28", "ph": "7.8–8.5", "do": "≥ 4", "sal": "20–35"},
}
DEFAULT_HINT = {"temp": "24–32", "ph": "7.0–9.0", "do": "≥ 4", "sal": "15–35"}


class PondThresholdForm(forms.ModelForm):
    class Meta:
        model = Pond
        fields = ["temp_min", "temp_max", "ph_min", "ph_max", "do_min", "salinity_min", "salinity_max"]
        widgets = {
            f: forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
            for f in ["temp_min", "temp_max", "ph_min", "ph_max", "do_min", "salinity_min", "salinity_max"]
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pond = kwargs.get("instance")
        hint = SPECIES_HINTS.get(pond.species, DEFAULT_HINT) if pond else DEFAULT_HINT

        self.fields["temp_min"].label = "水溫下限 (°C)"
        self.fields["temp_min"].help_text = f"建議 {hint['temp']}°C"
        self.fields["temp_max"].label = "水溫上限 (°C)"
        self.fields["temp_max"].help_text = f"建議 {hint['temp']}°C"
        self.fields["ph_min"].label = "pH 下限"
        self.fields["ph_min"].help_text = f"建議 {hint['ph']}"
        self.fields["ph_max"].label = "pH 上限"
        self.fields["ph_max"].help_text = f"建議 {hint['ph']}"
        self.fields["do_min"].label = "溶氧下限 (mg/L)"
        self.fields["do_min"].help_text = f"建議 {hint['do']} mg/L"
        self.fields["salinity_min"].label = "鹽度下限 (ppt)"
        self.fields["salinity_min"].help_text = f"建議 {hint['sal']} ppt"
        self.fields["salinity_max"].label = "鹽度上限 (ppt)"
        self.fields["salinity_max"].help_text = f"建議 {hint['sal']} ppt"

    def clean(self):
        data = super().clean()
        if data.get("temp_min") and data.get("temp_max") and data["temp_min"] >= data["temp_max"]:
            self.add_error("temp_max", "水溫上限必須大於下限")
        if data.get("ph_min") and data.get("ph_max") and data["ph_min"] >= data["ph_max"]:
            self.add_error("ph_max", "pH 上限必須大於下限")
        if data.get("salinity_min") and data.get("salinity_max") and data["salinity_min"] >= data["salinity_max"]:
            self.add_error("salinity_max", "鹽度上限必須大於下限")
        return data
