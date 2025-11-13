from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from main.models import Product

class Discount(models.Model):
    DISCOUNT_TYPES = (
        ('percentage', 'Відсоток'),
        ('fixed', 'Фіксована сума'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discounts')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    min_quantity = models.IntegerField(default=1)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Знижка'
        verbose_name_plural = 'Знижки'

    def __str__(self):
        return f"{self.product.name} — {self.discount_type} ({self.value})"

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date
        )

    def calculate_discount(self, price, quantity=1):
        if not self.is_valid() or quantity < self.min_quantity:
            return 0

        if self.discount_type == 'percentage':
            return price * (self.value / 100)

        elif self.discount_type == 'fixed':
            return min(self.value, price)

        return 0

    def get_discounted_price(self, price, quantity=1):
        discount = self.calculate_discount(price, quantity)
        return max(price - discount, 0)

    def clean(self):
        if self.discount_type == 'percentage':
            if not (0 < self.value <= 100):
                raise ValidationError('Відсоток знижки повинен бути між 0 і 100.')

        if self.discount_type == 'fixed':
            if self.value <= 0:
                raise ValidationError('Фіксована знижка повинна бути більше 0.')

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError('Дата закінчення повинна бути після дати початку.')

class PromoCode(models.Model):
    DISCOUNT_TYPES = (
        ('percentage', 'Відсоток'),
        ('fixed', 'Фіксована сума'),
        ('free_shipping', 'Безкоштовна доставка'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)

    min_order_amount = models.DecimalField( max_digits=10, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоди'

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return (self.is_active and self.start_date <= now <= self.end_date and self.can_be_used())

    def can_be_used(self):
        if self.usage_limit is None:
            return True
        return self.used_count < self.usage_limit

    def apply_discount(self, order_amount):
        if not self.is_valid():
            return order_amount

        if order_amount < self.min_order_amount:
            return order_amount

        if self.discount_type == 'percentage':
            discount = float(order_amount) * float((self.value / 100))
            return max(float(order_amount) - float(discount), 0)

        elif self.discount_type == 'fixed':
            discount = min(self.value, order_amount)
            return max(float(order_amount) - float(discount), 0)

        elif self.discount_type == 'free_shipping':
            return order_amount

        return order_amount

    def increment_usage(self):
        self.used_count += 1
        self.save()

    def clean(self):
        self.code = self.code.upper().replace(' ', '')

        if self.discount_type == 'percentage':
            if not (0 < self.value <= 100):
                raise ValidationError('Відсоток знижки повинен бути між 0 і 100.')

        if self.discount_type == 'fixed' and self.value <= 0:
            raise ValidationError('Фіксована сума повинна бути більше 0.')

        if self.end_date < self.start_date:
            raise ValidationError('Дата закінчення повинна бути після дати початку.')


class PromoCodeUsage(models.Model):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="promo_usages")
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-used_at"]
        verbose_name = "Використання промокоду"
        verbose_name_plural = "Використання промокодів"

    def __str__(self):
        return f"{self.promo_code.code} — {self.user.username} — {self.used_at.strftime('%Y-%m-%d')}"