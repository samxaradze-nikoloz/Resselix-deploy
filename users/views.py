from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from blog.models import Post

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'users/register.html', {'form': form})

            user = form.save(commit=False)
            user.save()

            messages.success(request, 'Account created! You can now log in')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            messages.success(request, "Profile updated successfully")
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })


def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    posts = Post.objects.filter(author=profile_user).order_by('-date_posted')

    return render(request, "users/public_profile.html", {
        "profile_user": profile_user,
        "user_posts": posts
    })

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_api(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = User.objects.create_user(
            username=request.data['username'],
            email=request.data.get('email'),
            password=request.data['password']
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailAPI(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user