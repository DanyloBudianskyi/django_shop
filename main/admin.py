from django.contrib import admin
from .models import Product, Category
from django.utils.html import format_html
from markdownx.admin import MarkdownxModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ( "id" ,"name", "slug", "is_active", "image_tag")
    list_editable = ( "name", "is_active")
    list_filter = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px" />',
                obj.image.url
            )
        return format_html('<span style="color: grey; width: 50px; height: 50px; border-radius: 4px">No image</span>')
    
    image_tag.short_description = "Image"

@admin.register(Product)
class ProductAdmin(MarkdownxModelAdmin):
    list_display = ( "id" ,"name", "category", "price", "is_available", "featured", "views", "image_tag" )
    list_editable = ( "price", "is_available", "featured")
    list_filter = ("created_at", "category", "is_available", "featured")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'category', 'image')
        }),
        ('Описи', {
            'fields': ('description',)
        }),
        ('Ціни', {
            'fields': ('price', 'discount_price')
        }),
        ('Налаштування', {
            'fields': ('is_available', 'featured', 'views')
        }),
    )

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px" />',
                obj.image.url
            )
        return format_html('<span style="color: grey; width: 50px; height: 50px; border-radius: 4px">No image</span>')
    
    image_tag.short_description = "Image"