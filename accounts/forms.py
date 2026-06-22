from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "帳號"
        self.fields["password"].label = "密碼"
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RegisterForm(UserCreationForm):
    nickname = forms.CharField(
        label="暱稱",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "養殖場主人的稱呼，例如：阿明"}),
    )

    class Meta:
        model = User
        fields = ["username", "nickname", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "帳號"
        self.fields["username"].widget.attrs["placeholder"] = "登入用帳號（英數字）"
        self.fields["password1"].label = "密碼"
        self.fields["password2"].label = "確認密碼"
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.nickname = self.cleaned_data["nickname"]
            user.profile.save()
        return user
