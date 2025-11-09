from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Avg, Count
from markdownx.models import MarkdownxField
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
    
    def __str__(self):
        return f"{self.name}"
    
    def get_absolute_url(self):
        return reverse("main:product_list_by_category", args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = MarkdownxField(blank = True, help_text="Детальний опис товару в форматі Markdown")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="products/%Y/%m/%d")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("main:product_detail", args=[self.id, self.slug])
    
    def get_average_rating(self):
        result = self.reviews.filter(is_active = True).aggregate(avg=Avg("rating"))
        return round(result["avg"], 1) if result["avg"] else 0
    
    def get_reviews_count(self):
        return self.reviews.filter(is_active = True).count()
    
    def get_rating_distribution(self):
        result = self.reviews.filter(is_active = True).values("rating").annotate(count=Count("rating"))

        distribution = {i: 0 for i in range(1,6)}
        
        for item in result:
            distribution[item["rating"]] = item["count"]

        return distribution
    
    def get_active_discount(self):
        now = timezone.now()
        discounts = self.discounts.filter(
            start_date__lte=now,
            end_date__gte=now
        )

        if not discounts.exists():
            return None
        
        prices = [
            (d, d.get_discounted_price(self.price, 1))
            for d in discounts
        ]
        best_discount = min(prices, key=lambda x: x[1])[0]
        return best_discount
    
    def get_discounted_price(self, quantity=1):
        discount = self.get_active_discount()

        if not discount:
            return self.price * quantity

        return discount.get_discounted_price(self.price, quantity)
    
    def has_active_discount(self):
        return self.get_active_discount() is not None
    
    def get_discount_percentage(self):
        discount = self.get_active_discount()
        if not discount:
            return 0

        original = self.price
        discounted = discount.get_discounted_price(original, 1)

        try:
            percentage = (1 - discounted / original) * 100
        except ZeroDivisionError:
            return 0

        return round(percentage, 2)