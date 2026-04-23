from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

class Post(models.Model):
    MAIN_CATEGORY_CHOICES = [
        ('accounts', 'Accounts'),
        ('sports', 'Sports'),
        ('fashion', 'Fashion'),
        ('electronics', 'Electronics'),
        ('home', 'Home'),
        ('misc', 'Miscellaneous'),
        ('accessories', 'Accessories'),
    ]

    SUBCATEGORY_CHOICES = [
        ('phone_cases', 'Phone Cases'), ('watches', 'Watches'), ('bags', 'Bags'), ('jewelry', 'Jewelry'),
        ('steam', 'Steam Account'), ('epic', 'Epic Games Account'), ('riot', 'Riot Games Account'),
        ('psn', 'PlayStation Account'), ('xbox', 'Xbox Account'), ('winter_sports', 'Winter Sports'),
        ('football', 'Football'), ('basketball', 'Basketball'), ('gym', 'Gym / Fitness'),
        ('men', 'Men Fashion'), ('women', 'Women Fashion'), ('shoes', 'Shoes'),
        ('phones', 'Phones'), ('laptops', 'Laptops'), ('tech_accessories', 'Tech Accessories'),
        ('furniture', 'Furniture'), ('decor', 'Decorations'),
    ]

    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.CharField(max_length=30, choices=MAIN_CATEGORY_CHOICES, default='misc')
    subcategory = models.CharField(max_length=30, choices=SUBCATEGORY_CHOICES, blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')

    def __str__(self):
        return f"Image for {self.post.title}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.quantity * self.post.price





class ForumPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE
    )

    def is_reply(self):
        return self.parent_id is not None

class Like(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')




class ForumComment(models.Model):
    post = models.ForeignKey(
    ForumPost,
    on_delete=models.CASCADE,
    related_name="forum_comments"
)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE
    )

class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"
