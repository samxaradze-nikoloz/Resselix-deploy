from .models import Report
from django.contrib.auth.models import User

def check_and_suspend_user(user):
    report_count = Report.objects.filter(reported_user=user).count()

    if report_count >= 5:
        user.is_active = False
        user.save()
        return True

    return False



from django.utils import timezone

def check_ban(user):
    if not hasattr(user, "profile"):
        return False

    profile = user.profile

    # auto-unban if time passed
    if profile.is_banned and profile.ban_until:
        if timezone.now() >= profile.ban_until:
            profile.is_banned = False
            profile.ban_until = None
            profile.save()

    return profile.is_banned


from .models import Profile

def decrease_trust(user, amount):
    profile = user.profile
    profile.trust_score = max(0, profile.trust_score - amount)
    profile.save()