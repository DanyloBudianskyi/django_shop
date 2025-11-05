from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = "Профіль"
    verbose_name_plural = "Профіль"

    fields = ('avatar', 'bio', 'birth_date', 'location', 'website', 'created_at', 'updated_at')
    
    readonly_fields=('created_at', 'updated_at')

    extra = 0
    classes = ('collapse',)

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'date_joined', 'get_location', 'get_profile_created'
    )
    search_fields = ('username', 'email', 'profile__location')

    def get_location(self, obj):
        return obj.profile.location if hasattr(obj, 'profile') and obj.profile.location else "-"
    get_location.short_description = "Місто"

    def get_profile_created(self, obj):
        return obj.profile.created_at if hasattr(obj, 'profile') else "-"
    get_profile_created.short_description = "Профіль створено"
    get_profile_created.admin_order_field = "profile__created_at"

class ProfileAdmin(admin.ModelAdmin):
    """Окрема адмінка для Profile"""
    list_display = ('user', 'location', 'birth_date', 'has_avatar', 'created_at')
    search_fields = ('user__username', 'user__email', 'location', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Користувач', {
            'fields': ('user',)
        }),
        ('Основна інформація', {
            'fields': ('avatar', 'bio', 'birth_date', 'location', 'website')
        }),
        ('Системна інформація', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    def has_avatar(self, obj):
        """Чи є аватар"""
        return bool(obj.avatar)
    has_avatar.boolean = True
    has_avatar.short_description = 'Аватар'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
