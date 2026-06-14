from django.db import models

# 水質安全範圍 — 用於儀表板異常提示與統計分析。
THRESHOLDS = {
    "temperature": {"label": "水溫", "unit": "°C", "min": 24, "max": 32, "icon": "bi-thermometer-half"},
    "ph": {"label": "pH 值", "unit": "", "min": 7.0, "max": 9.0, "icon": "bi-droplet-half"},
    "dissolved_oxygen": {"label": "溶氧", "unit": "mg/L", "min": 4.0, "max": None, "icon": "bi-wind"},
    "salinity": {"label": "鹽度", "unit": "ppt", "min": 15, "max": 35, "icon": "bi-water"},
}


def threshold_range_text(rule):
    if rule["min"] is not None and rule["max"] is not None:
        return f"{rule['min']}–{rule['max']}{rule['unit']}"
    if rule["min"] is not None:
        return f"≥ {rule['min']}{rule['unit']}"
    return f"≤ {rule['max']}{rule['unit']}"


class Pond(models.Model):
    """養殖池基本資料。"""

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    species = models.CharField(max_length=50, default="文蛤")

    def __str__(self):
        return self.name


class SensorReading(models.Model):
    """感測器讀值 — 一次量到的水質快照。"""

    pond = models.ForeignKey(Pond, on_delete=models.CASCADE, related_name="readings")
    measured_at = models.DateTimeField(db_index=True)

    temperature = models.FloatField(help_text="水溫 °C")
    ph = models.FloatField(help_text="pH 值")
    dissolved_oxygen = models.FloatField(help_text="溶氧 mg/L")
    salinity = models.FloatField(help_text="鹽度 ppt", null=True, blank=True)

    class Meta:
        ordering = ["-measured_at"]
        indexes = [models.Index(fields=["pond", "-measured_at"])]

    def __str__(self):
        return f"{self.pond.name} @ {self.measured_at:%Y-%m-%d %H:%M}"

    def get_alerts(self):
        """回傳超出安全範圍的指標清單，每項含數值、範圍與提示訊息。"""
        alerts = []
        for field, rule in THRESHOLDS.items():
            value = getattr(self, field, None)
            if value is None:
                continue
            too_low = rule["min"] is not None and value < rule["min"]
            too_high = rule["max"] is not None and value > rule["max"]
            if not (too_low or too_high):
                continue
            alerts.append(
                {
                    "metric": field,
                    "label": rule["label"],
                    "value": value,
                    "unit": rule["unit"],
                    "range": threshold_range_text(rule),
                    "level": "low" if too_low else "high",
                    "message": (
                        f"{rule['label']}{'過低' if too_low else '過高'}："
                        f"目前 {value}{rule['unit']}，正常範圍為 {threshold_range_text(rule)}"
                    ),
                }
            )
        return alerts

    @property
    def is_normal(self):
        return not self.get_alerts()

    def reading_cards(self):
        """回傳各指標的顯示用資料：數值、單位、安全範圍與是否異常，供模板顯示。"""
        alerts_by_metric = {alert["metric"]: alert for alert in self.get_alerts()}
        cards = []
        for field, rule in THRESHOLDS.items():
            cards.append(
                {
                    "field": field,
                    "label": rule["label"],
                    "unit": rule["unit"],
                    "icon": rule["icon"],
                    "value": getattr(self, field, None),
                    "range_text": threshold_range_text(rule),
                    "alert": alerts_by_metric.get(field),
                }
            )
        return cards
