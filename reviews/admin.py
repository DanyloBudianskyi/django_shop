from django.contrib import admin
from .models import Review


@admin.action(description="Активувати відгуки")
def activate_reviews(self, request, queryset):
    updated = queryset.update(is_active=True)
    self.message_user(request, f"{updated} відгуків активовано.")


@admin.action(description="Деактивувати відгуки")
def deactivate_reviews(self, request, queryset):
    updated = queryset.update(is_active=False)
    self.message_user(request, f"{updated} відгуків деактивовано.")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "product", "rating", "title_preview", "created_at", "is_active", "helpful_count")
    list_filter = ("rating", "is_active", "created_at")
    search_fields = ("author__username", "product__name", "title", "content")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("is_active",)

    fieldsets = (
        ("Основна інформація", {
            "fields": ("product", "author", "rating", "title", "content")
        }),
        ("Деталі", {
            "fields": ("advantages", "disadvantages")
        }),
        ("Системні", {
            "fields": ("is_active", "helpful_count", "created_at", "updated_at")
        }),
    )

    actions = [activate_reviews, deactivate_reviews]

    @admin.display(description="Заголовок")
    def title_preview(self, obj):
        return obj.title[:50] + ("…" if len(obj.title) > 50 else "")
