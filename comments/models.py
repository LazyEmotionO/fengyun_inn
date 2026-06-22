from django.conf import settings
from django.db import models


class Comment(models.Model):
    BOARD_CHOICES = [
        ("ar", "AR 排行榜"),
        ("water", "智慧養殖"),
    ]

    board = models.CharField(max_length=10, choices=BOARD_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField("留言內容", blank=True)
    image = models.ImageField("留言圖片", upload_to="comments/%Y/%m/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} @ {self.board}: {self.text[:30]}"
