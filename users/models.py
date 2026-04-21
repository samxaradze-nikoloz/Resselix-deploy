from django.db import models
from django.contrib.auth.models import User
from blog.models import Post 
from PIL import Image
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
import os
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Ratings
    average_rating = models.FloatField(default=0)

    # Ban system
    is_banned = models.BooleanField(default=False)
    ban_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    def is_currently_banned(self):
        if self.is_banned and self.ban_until:
            if timezone.now() > self.ban_until:
                self.is_banned = False
                self.ban_until = None
                self.save(update_fields=["is_banned", "ban_until"])
        return self.is_banned

    @property
    def trust_score(self):
        return round((self.average_rating / 5) * 100, 1) if self.average_rating else 0


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image and os.path.exists(self.image.path):
            img = Image.open(self.image.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    
class Review(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        avg = Review.objects.filter(seller=self.seller).aggregate(avg=Avg("rating"))["avg"]

        profile = self.seller.profile
        profile.average_rating = avg or 0
        profile.save(update_fields=["average_rating"])

    def __str__(self):
        return f"Review for {self.seller.username} by {self.author.username}"
    

from django.contrib.auth.models import User
from django.db import models

class Report(models.Model):
    REASON_CHOICES = [
        ("spam", "Spam"),
        ("scam", "Scam"),
        ("abuse", "Abuse"),
        ("other", "Other"),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_received")

    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    is_reviewed = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.reporter} → {self.reported_user}"


