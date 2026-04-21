from django.shortcuts import redirect
from django.contrib.auth import logout
from .utils import check_ban

class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            if check_ban(user):
                logout(request)
                return redirect("login")

        return self.get_response(request)