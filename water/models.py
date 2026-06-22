from django.db import models

# 全局預設值 — 作為新建池塘的初始門檻，也供表單初始值參考。
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
    """養殖池基本資料，含各池專屬水質安全門檻。"""

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    species = models.CharField(max_length=50, default="文蛤")

    # 各池專屬門檻 — 預設值對應全局 THRESHOLDS
    temp_min = models.FloatField("水溫下限 (°C)", default=24)
    temp_max = models.FloatField("水溫上限 (°C)", default=32)
    ph_min = models.FloatField("pH 下限", default=7.0)
    ph_max = models.FloatField("pH 上限", default=9.0)
    do_min = models.FloatField("溶氧下限 (mg/L)", default=4.0)
    salinity_min = models.FloatField("鹽度下限 (ppt)", default=15)
    salinity_max = models.FloatField("鹽度上限 (ppt)", default=35)

    def __str__(self):
        return self.name

    def get_thresholds(self):
        """回傳此池塘的門檻 dict，格式與全局 THRESHOLDS 相同。"""
        return {
            "temperature": {
                "label": "水溫", "unit": "°C",
                "min": self.temp_min, "max": self.temp_max,
                "icon": "bi-thermometer-half",
            },
            "ph": {
                "label": "pH 值", "unit": "",
                "min": self.ph_min, "max": self.ph_max,
                "icon": "bi-droplet-half",
            },
            "dissolved_oxygen": {
                "label": "溶氧", "unit": "mg/L",
                "min": self.do_min, "max": None,
                "icon": "bi-wind",
            },
            "salinity": {
                "label": "鹽度", "unit": "ppt",
                "min": self.salinity_min, "max": self.salinity_max,
                "icon": "bi-water",
            },
        }


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

    def get_alerts(self, thresholds=None):
        """回傳超出安全範圍的指標清單。thresholds 預設取此池塘的專屬門檻。"""
        if thresholds is None:
            thresholds = self.pond.get_thresholds()
        alerts = []
        for field, rule in thresholds.items():
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

    def health_score(self, thresholds=None):
        """
        計算水質健康分數 0–100。
        各指標在範圍內得 100 分，超出則依距離邊界的比例扣分。
        最終分數 = 各指標平均 × 0.7 + 最差指標分數 × 0.3，
        讓單一嚴重異常也能明顯拉低總分。
        """
        if thresholds is None:
            thresholds = self.pond.get_thresholds()

        scores = []
        for field, rule in thresholds.items():
            value = getattr(self, field, None)
            if value is None:
                continue
            lo, hi = rule["min"], rule["max"]

            # 容忍幅度：有上下限時為範圍寬度的一半；只有單邊時為該限值的一半
            if lo is not None and hi is not None:
                tol = max((hi - lo) * 0.5, 0.1)
            elif lo is not None:
                tol = max(lo * 0.5, 0.1)
            else:
                tol = max(hi * 0.5, 0.1)

            if lo is not None and value < lo:
                scores.append(max(0.0, 100 * (1 - (lo - value) / tol)))
            elif hi is not None and value > hi:
                scores.append(max(0.0, 100 * (1 - (value - hi) / tol)))
            else:
                scores.append(100.0)

        if not scores:
            return 0
        avg = sum(scores) / len(scores)
        worst = min(scores)
        return round(avg * 0.7 + worst * 0.3)

    def reading_cards(self, thresholds=None):
        """回傳各指標顯示用資料，供模板使用。"""
        if thresholds is None:
            thresholds = self.pond.get_thresholds()
        alerts_by_metric = {a["metric"]: a for a in self.get_alerts(thresholds=thresholds)}
        return [
            {
                "field": field,
                "label": rule["label"],
                "unit": rule["unit"],
                "icon": rule["icon"],
                "value": getattr(self, field, None),
                "range_text": threshold_range_text(rule),
                "alert": alerts_by_metric.get(field),
            }
            for field, rule in thresholds.items()
        ]
