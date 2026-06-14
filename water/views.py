import json
from datetime import timedelta

from django.shortcuts import get_object_or_404, render
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone

from .models import THRESHOLDS, Pond, threshold_range_text

DAY_OPTIONS = [1, 7, 14, 30]


def dashboard(request):
    ponds = Pond.objects.all()

    pond_data = []
    alert_count = 0
    normal_count = 0
    for pond in ponds:
        latest = pond.readings.first()
        alerts = latest.get_alerts() if latest else []
        if latest:
            if alerts:
                alert_count += 1
            else:
                normal_count += 1
        pond_data.append({"pond": pond, "latest": latest, "alerts": alerts})

    context = {
        "pond_data": pond_data,
        "total_ponds": ponds.count(),
        "normal_count": normal_count,
        "alert_count": alert_count,
        "thresholds": THRESHOLDS,
        "updated_at": timezone.now(),
    }
    return render(request, "water/dashboard.html", context)


def pond_detail(request, pond_id):
    pond = get_object_or_404(Pond, pk=pond_id)

    try:
        days = int(request.GET.get("days", 7))
    except ValueError:
        days = 7
    if days not in DAY_OPTIONS:
        days = 7

    since = timezone.now() - timedelta(days=days)
    readings = list(pond.readings.filter(measured_at__gte=since).order_by("measured_at"))

    latest = pond.readings.first()
    alerts = latest.get_alerts() if latest else []

    stats = pond.readings.filter(measured_at__gte=since).aggregate(
        temperature_avg=Avg("temperature"),
        temperature_min=Min("temperature"),
        temperature_max=Max("temperature"),
        ph_avg=Avg("ph"),
        ph_min=Min("ph"),
        ph_max=Max("ph"),
        dissolved_oxygen_avg=Avg("dissolved_oxygen"),
        dissolved_oxygen_min=Min("dissolved_oxygen"),
        dissolved_oxygen_max=Max("dissolved_oxygen"),
        salinity_avg=Avg("salinity"),
        salinity_min=Min("salinity"),
        salinity_max=Max("salinity"),
        count=Count("id"),
    )

    anomaly_count = sum(1 for reading in readings if reading.get_alerts())

    chart_labels = [
        timezone.localtime(reading.measured_at).strftime("%m/%d %H:%M") for reading in readings
    ]
    chart_series = {
        "temperature": [reading.temperature for reading in readings],
        "ph": [reading.ph for reading in readings],
        "dissolved_oxygen": [reading.dissolved_oxygen for reading in readings],
        "salinity": [reading.salinity for reading in readings],
    }

    metric_rows = []
    for field, rule in THRESHOLDS.items():
        avg = stats.get(f"{field}_avg")
        avg_status = "no_data"
        analysis = "近期尚無資料"
        if avg is not None:
            too_low = rule["min"] is not None and avg < rule["min"]
            too_high = rule["max"] is not None and avg > rule["max"]
            if too_low:
                avg_status = "low"
                analysis = f"期間平均值低於安全下限（{threshold_range_text(rule)}），建議留意是否持續偏低"
            elif too_high:
                avg_status = "high"
                analysis = f"期間平均值高於安全上限（{threshold_range_text(rule)}），建議留意是否持續偏高"
            else:
                avg_status = "normal"
                analysis = f"期間平均值在安全範圍內（{threshold_range_text(rule)}），狀況穩定"
        metric_rows.append(
            {
                "field": field,
                "label": rule["label"],
                "unit": rule["unit"],
                "icon": rule["icon"],
                "avg": avg,
                "min": stats.get(f"{field}_min"),
                "max": stats.get(f"{field}_max"),
                "range_text": threshold_range_text(rule),
                "avg_status": avg_status,
                "analysis": analysis,
            }
        )

    reading_count = stats["count"]
    anomaly_pct = round(anomaly_count / reading_count * 100, 1) if reading_count else 0

    context = {
        "pond": pond,
        "latest": latest,
        "alerts": alerts,
        "metric_rows": metric_rows,
        "reading_count": reading_count,
        "anomaly_count": anomaly_count,
        "anomaly_pct": anomaly_pct,
        "days": days,
        "day_options": DAY_OPTIONS,
        "thresholds": THRESHOLDS,
        "chart_labels_json": json.dumps(chart_labels, ensure_ascii=False),
        "chart_temperature_json": json.dumps(chart_series["temperature"]),
        "chart_ph_json": json.dumps(chart_series["ph"]),
        "chart_dissolved_oxygen_json": json.dumps(chart_series["dissolved_oxygen"]),
        "chart_salinity_json": json.dumps(chart_series["salinity"]),
    }
    return render(request, "water/pond_detail.html", context)
