import csv
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone

from .forms import PondThresholdForm
from .models import THRESHOLDS, Pond, SensorReading, threshold_range_text

DAY_OPTIONS = [1, 7, 14, 30, 0]  # 0 = 全部資料


def _score_class(score):
    if score is None:
        return "secondary"
    if score >= 80:
        return "success"
    if score >= 60:
        return "warning"
    return "danger"


@login_required
def dashboard(request):
    ponds = Pond.objects.filter(owner=request.user)

    pond_data = []
    alert_count = 0
    normal_count = 0
    for pond in ponds:
        thresholds = pond.get_thresholds()
        latest = pond.readings.select_related("pond").first()
        alerts = latest.get_alerts(thresholds=thresholds) if latest else []
        score = latest.health_score(thresholds=thresholds) if latest else None
        if latest:
            if alerts:
                alert_count += 1
            else:
                normal_count += 1
        pond_data.append({
            "pond": pond,
            "latest": latest,
            "alerts": alerts,
            "health_score": score,
            "score_class": _score_class(score),
        })

    context = {
        "pond_data": pond_data,
        "total_ponds": ponds.count(),
        "normal_count": normal_count,
        "alert_count": alert_count,
        "updated_at": timezone.now(),
    }
    return render(request, "water/dashboard.html", context)


@login_required
def pond_detail(request, pond_id):
    pond = get_object_or_404(Pond, pk=pond_id, owner=request.user)
    thresholds = pond.get_thresholds()

    try:
        days = int(request.GET.get("days", 30))
    except ValueError:
        days = 30
    if days not in DAY_OPTIONS:
        days = 30

    if days == 0:
        qs = pond.readings.select_related("pond").order_by("measured_at")
        stats_qs = pond.readings
    else:
        since = timezone.now() - timedelta(days=days)
        qs = pond.readings.select_related("pond").filter(measured_at__gte=since).order_by("measured_at")
        stats_qs = qs

    readings = list(qs)

    latest = pond.readings.select_related("pond").first()
    alerts = latest.get_alerts(thresholds=thresholds) if latest else []
    score = latest.health_score(thresholds=thresholds) if latest else None

    stats = stats_qs.aggregate(
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

    anomaly_count = sum(1 for r in readings if r.get_alerts(thresholds=thresholds))

    chart_labels = [
        timezone.localtime(r.measured_at).strftime("%m/%d %H:%M") for r in readings
    ]
    chart_series = {
        "temperature": [r.temperature for r in readings],
        "ph": [r.ph for r in readings],
        "dissolved_oxygen": [r.dissolved_oxygen for r in readings],
        "salinity": [r.salinity for r in readings],
    }

    metric_rows = []
    for field, rule in thresholds.items():
        avg = stats.get(f"{field}_avg")
        avg_status = "no_data"
        analysis = "所選區間尚無資料"
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
        metric_rows.append({
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
        })

    reading_count = stats["count"]
    anomaly_pct = round(anomaly_count / reading_count * 100, 1) if reading_count else 0

    context = {
        "pond": pond,
        "latest": latest,
        "alerts": alerts,
        "health_score": score,
        "score_class": _score_class(score),
        "metric_rows": metric_rows,
        "reading_count": reading_count,
        "anomaly_count": anomaly_count,
        "anomaly_pct": anomaly_pct,
        "days": days,
        "day_options": DAY_OPTIONS,
        "thresholds": thresholds,
        "chart_labels_json": json.dumps(chart_labels, ensure_ascii=False),
        "chart_temperature_json": json.dumps(chart_series["temperature"]),
        "chart_ph_json": json.dumps(chart_series["ph"]),
        "chart_dissolved_oxygen_json": json.dumps(chart_series["dissolved_oxygen"]),
        "chart_salinity_json": json.dumps(chart_series["salinity"]),
    }
    return render(request, "water/pond_detail.html", context)


@login_required
def edit_thresholds(request, pond_id):
    pond = get_object_or_404(Pond, pk=pond_id, owner=request.user)
    if request.method == "POST":
        form = PondThresholdForm(request.POST, instance=pond)
        if form.is_valid():
            form.save()
            messages.success(request, f"{pond.name} 的水質安全門檻已更新。")
            return redirect("water:pond_detail", pond_id=pond.id)
    else:
        form = PondThresholdForm(instance=pond)
    return render(request, "water/edit_thresholds.html", {"pond": pond, "form": form})


@login_required
def alerts_list(request):
    pond_id = request.GET.get("pond")
    selected_pond = None
    own_ponds = Pond.objects.filter(owner=request.user)

    if pond_id:
        try:
            selected_pond = get_object_or_404(Pond, pk=int(pond_id), owner=request.user)
            base_qs = selected_pond.readings.select_related("pond")
        except (ValueError, TypeError):
            base_qs = SensorReading.objects.filter(pond__owner=request.user).select_related("pond")
    else:
        base_qs = SensorReading.objects.filter(pond__owner=request.user).select_related("pond")

    anomaly_readings = []
    for reading in base_qs.order_by("-measured_at")[:600]:
        thresholds = reading.pond.get_thresholds()
        a = reading.get_alerts(thresholds=thresholds)
        if a:
            anomaly_readings.append({"reading": reading, "alerts": a})
        if len(anomaly_readings) >= 100:
            break

    context = {
        "anomaly_readings": anomaly_readings,
        "ponds": own_ponds,
        "selected_pond": selected_pond,
    }
    return render(request, "water/alerts.html", context)


@login_required
def export_csv(request, pond_id):
    pond = get_object_or_404(Pond, pk=pond_id, owner=request.user)
    thresholds = pond.get_thresholds()

    try:
        days = int(request.GET.get("days", 0))
    except ValueError:
        days = 0
    if days not in DAY_OPTIONS:
        days = 0

    if days == 0:
        qs = pond.readings.select_related("pond").order_by("measured_at")
    else:
        since = timezone.now() - timedelta(days=days)
        qs = pond.readings.select_related("pond").filter(measured_at__gte=since).order_by("measured_at")

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="{pond.name}_water_quality.csv"'

    writer = csv.writer(response)
    writer.writerow(["時間", "水溫(°C)", "pH值", "溶氧(mg/L)", "鹽度(ppt)", "健康分數", "狀態"])
    for reading in qs:
        status = "正常" if not reading.get_alerts(thresholds=thresholds) else "異常"
        writer.writerow([
            timezone.localtime(reading.measured_at).strftime("%Y/%m/%d %H:%M"),
            reading.temperature,
            reading.ph,
            reading.dissolved_oxygen,
            reading.salinity if reading.salinity is not None else "",
            reading.health_score(thresholds=thresholds),
            status,
        ])

    return response
