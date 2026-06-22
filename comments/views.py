from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CommentForm
from .models import Comment

VALID_BOARDS = {choice[0] for choice in Comment.BOARD_CHOICES}


@require_POST
@login_required
def add_comment(request, board):
    if board not in VALID_BOARDS:
        raise Http404

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = "/"

    form = CommentForm(request.POST, request.FILES)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.board = board
        comment.user = request.user
        comment.save()
    else:
        errors = " ".join(e for field_errors in form.errors.values() for e in field_errors)
        messages.error(request, errors or "留言送出失敗，請再試一次。")

    return redirect(next_url)
