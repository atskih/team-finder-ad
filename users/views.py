from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.services import paginate_queryset

from .constants import USERS_PER_PAGE
from .forms import LoginForm, ProfileForm, RegisterForm, UserPasswordChangeForm
from .models import User


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request, request.POST or None)
    if form.is_valid():
        login(request, form.user)
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def participants(request):
    users = User.objects.order_by("-date_joined", "-id")
    page_obj = paginate_queryset(request, users, USERS_PER_PAGE)
    return render(request, "users/participants.html", {"participants": page_obj, "page_obj": page_obj})


def user_details(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    data = request.POST or None
    files = request.FILES or None
    form = ProfileForm(data, files, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("users:details", user_id=request.user.id)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:details", user_id=request.user.id)
    return render(request, "users/change_password.html", {"form": form})
