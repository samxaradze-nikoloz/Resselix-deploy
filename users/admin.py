from django.contrib import admin
from .models import Report
from .models import Profile
from django.utils import timezone
from datetime import timedelta

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reported_user", "reporter", "created_at", "resolved")
    list_filter = ("resolved", "created_at")
    search_fields = ("reported_user__username", "reporter__username", "reason")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_banned", "ban_until")
    actions = ["ban_24h", "ban_7d", "ban_perm", "unban"]

    def ban_24h(self, request, queryset):
        queryset.update(is_banned=True, ban_until=timezone.now() + timedelta(days=1))

    def ban_7d(self, request, queryset):
        queryset.update(is_banned=True, ban_until=timezone.now() + timedelta(days=7))

    def ban_perm(self, request, queryset):
        queryset.update(is_banned=True, ban_until=None)

    def unban(self, request, queryset):
        queryset.update(is_banned=False, ban_until=None)