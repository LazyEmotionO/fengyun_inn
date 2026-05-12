from django import forms
from crispy_forms.helper import FormHelper
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # prevent crispy from wrapping in <form> tags

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '您的姓名'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '選填'}),
            'subject': forms.TextInput(attrs={'placeholder': '訊息主旨'}),
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': '請輸入您的訊息...'}),
        }
        labels = {
            'name': '姓名',
            'email': '電子郵件',
            'phone': '電話（選填）',
            'subject': '主旨',
            'message': '訊息內容',
        }
