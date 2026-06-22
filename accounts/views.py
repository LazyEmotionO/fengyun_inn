from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect, render

from water.provisioning import create_starter_ponds

from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("water:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_starter_ponds(user)
            login(request, user)
            messages.success(request, f"歡迎加入，{user.profile.nickname}！已為您建立示範養殖場。")
            return redirect("water:dashboard")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})
