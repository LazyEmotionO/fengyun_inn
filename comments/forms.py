from django import forms

from .models import Comment

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text", "image"]
        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "輸入留言，也可以直接 Ctrl+V 貼上截圖...",
                "class": "form-control comment-textarea",
            }),
            "image": forms.ClearableFileInput(attrs={
                "accept": "image/*",
                "class": "comment-image-input",
                "hidden": True,
            }),
        }

    def clean(self):
        cleaned = super().clean()
        text = cleaned.get("text", "").strip()
        image = cleaned.get("image")
        if not text and not image:
            raise forms.ValidationError("請輸入留言內容或上傳圖片。")
        if image and image.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError("圖片大小請勿超過 5MB。")
        return cleaned
