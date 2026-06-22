"""新帳號註冊時，自動建立含示範資料的養殖場（池塘）。"""

import random
from datetime import timedelta

from django.utils import timezone

from .models import Pond, SensorReading

STARTER_PONDS = [
    {"name": "1 號池", "species": "文蛤", "description": "靠近進水口的小池"},
    {"name": "2 號池", "species": "白蝦", "description": "去年底新挖的池"},
]

DAYS_BACK = 7
READINGS_PER_DAY = 4


def create_starter_ponds(user):
    """為新帳號建立示範池塘與近 7 天的模擬感測資料。"""
    now = timezone.now().replace(minute=0, second=0, microsecond=0)
    rng = random.Random(user.pk)

    ponds = [Pond.objects.create(owner=user, **spec) for spec in STARTER_PONDS]

    for pond in ponds:
        for day_offset in range(DAYS_BACK):
            day = now - timedelta(days=day_offset)
            for slot in range(READINGS_PER_DAY):
                measured_at = day.replace(hour=6 + slot * 5)
                SensorReading.objects.create(
                    pond=pond,
                    measured_at=measured_at,
                    temperature=round(rng.uniform(26, 30), 1),
                    ph=round(rng.uniform(7.5, 8.6), 2),
                    dissolved_oxygen=round(rng.uniform(5.5, 7.5), 1),
                    salinity=round(rng.uniform(20, 32), 1),
                )

    return ponds
