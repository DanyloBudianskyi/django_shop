from django.contrib import admin
from django.utils.html import format_html
from .models import Discount, PromoCode, PromoCodeUsage

@admin.action(description="Активувати вибрані знижки")
def activate_discounts(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description="Деактивувати вибрані знижки")
def deactivate_discounts(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('product', 'discount_type', 'value', 'start_date', 'end_date', 'is_active', 'is_valid_now')
    list_filter = ('discount_type', 'is_active', 'start_date')
    search_fields = ('product__name', 'description')
    readonly_fields = ('created_at',)
    list_editable = ('is_active',)
    date_hierarchy = 'start_date'
    actions = [activate_discounts, deactivate_discounts]

    def is_valid_now(self, obj):
        return obj.is_valid()
    is_valid_now.boolean = True
    is_valid_now.short_description = "Активна зараз?"

@admin.action(description="Активувати вибрані промокоди")
def activate_codes(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description="Деактивувати вибрані промокоди")
def deactivate_codes(modeladmin, request, queryset):
    queryset.update(is_active=False)

@admin.action(description="Скинути використання промокодів")
def reset_usage(modeladmin, request, queryset):
    for promo in queryset:
        promo.used_count = 0
        promo.save()

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'usage_progress', 'valid_period', 'is_active', 'created_by')
    list_filter = ('discount_type', 'is_active', 'created_at')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at')
    actions = [activate_codes, deactivate_codes, reset_usage]

    fieldsets = (
        (None, {
            'fields': ('code', 'discount_type', 'value', 'description')
        }),
        ('Деталі використання', {
            'fields': ('start_date', 'end_date', 'usage_limit', 'used_count', 'min_order_amount', 'is_active', 'created_by')
        }),
    )

    def usage_progress(self, obj):
        if obj.usage_limit:
            percent = int(obj.used_count / obj.usage_limit * 100)
            return format_html(
                '<progress value="{}" max="100">{}</progress> {}%',
                percent, percent, percent
            )
        return "∞"
    usage_progress.short_description = "Використання"

    def valid_period(self, obj):
        return f"{obj.start_date.strftime('%d.%m.%Y')} - {obj.end_date.strftime('%d.%m.%Y')}"
    valid_period.short_description = "Період дії"



@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ('promo_code', 'user', 'order_amount', 'discount_amount', 'used_at')
    list_filter = ('used_at', 'promo_code')
    search_fields = ('user__username', 'promo_code__code')
    readonly_fields = ('promo_code', 'user', 'order_amount', 'discount_amount', 'used_at')
    date_hierarchy = 'used_at'
