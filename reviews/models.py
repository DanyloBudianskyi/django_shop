from django.db import models
from django.contrib.auth.models import User

from main.models import Product

# Create your models here.
class Review(models.Model):
    RATING_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    advantages = models.TextField(blank=True)
    disadvantages = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    helpful_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        unique_together = ['product', 'author']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product} - {self.author}"
    
    def get_rating_display_stars(self):
        full_stars = "★" * self.rating
        empty_stars = "☆" * (5 - self.rating)
        return full_stars + empty_stars