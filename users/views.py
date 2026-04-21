from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.utils import timezone

from rest_framework import generics, permissions

from blog.models import Post
from .models import Profile, Review
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .serializers import UserSerializer
from django.contrib.admin.views.decorators import staff_member_required

def check_ban(user):
    if hasattr(user, "profile"):
        profile = user.profile

        if profile.is_banned and profile.ban_until:
            if timezone.now() > profile.ban_until:
                profile.is_banned = False
                profile.ban_until = None
                profile.save()

        return profile.is_banned

    return False


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            messages.success(request, "Account created! You can now log in")
            return redirect("login")

    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request):
    if check_ban(request.user):
        logout(request)
        messages.error(request, "Your account is suspended.")
        return redirect("login")

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("profile")

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, "users/profile.html", {
        "u_form": u_form,
        "p_form": p_form
    })


def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    user_posts = Post.objects.filter(author=profile_user).order_by("-date_posted")
    reviews = Review.objects.filter(seller=profile_user).order_by("-id")

    if hasattr(profile_user, "profile") and check_ban(profile_user):
        return render(request, "users/public_profile.html", {
            "profile_user": profile_user,
            "user_posts": [],
            "reviews": [],
            "banned": True
        })

    if request.method == "POST" and request.user.is_authenticated:
        if request.user != profile_user:

            rating = request.POST.get("rating")
            content = request.POST.get("content")

            if rating:
                Review.objects.update_or_create(
                    author=request.user,
                    seller=profile_user,
                    defaults={
                        "rating": int(rating),
                        "content": content
                    }
                )

            return redirect("public-profile", username=username)

    return render(request, "users/public_profile.html", {
        "profile_user": profile_user,
        "user_posts": user_posts,
        "reviews": reviews
    })


class ProfileDetailAPI(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    


from .models import Report
from django.contrib.auth.models import User

def report_user(request, username):
    reported_user = get_object_or_404(User, username=username)

    if request.method == "POST":
        reason = request.POST.get("reason")

        if request.user.is_authenticated and reason:
            Report.objects.create(
                reported_user=reported_user,
                reporter=request.user,
                reason=reason
            )

        return redirect("public-profile", username=username)
    messages.success(request, "Report submitted successfully")

    return render(request, "users/report_user.html", {
        "reported_user": reported_user
    })



from .utils import check_ban
from datetime import timedelta

@staff_member_required
def ban_user(request, username):
    user = get_object_or_404(User, username=username)
    duration = request.POST.get("duration")

    profile = user.profile
    profile.is_banned = True

    if duration == "1h":
        profile.ban_until = timezone.now() + timedelta(hours=1)

    elif duration == "24h":
        profile.ban_until = timezone.now() + timedelta(days=1)

    elif duration == "7d":
        profile.ban_until = timezone.now() + timedelta(days=7)

    elif duration == "30d":
        profile.ban_until = timezone.now() + timedelta(days=30)

    elif duration == "perm":
        profile.ban_until = None  # permanent ban

    profile.save()

    return redirect("public-profile", username=username)