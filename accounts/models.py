from django.conf import settings
from django.db import models


class Profile(models.Model):
    """每個帳號的附加資料：暱稱、AR 累積分數。"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    nickname = models.CharField("暱稱", max_length=30, blank=True, default="")
    ar_score = models.PositiveIntegerField("AR 累積分數", default=0)

    def __str__(self):
        return self.nickname or self.user.username
