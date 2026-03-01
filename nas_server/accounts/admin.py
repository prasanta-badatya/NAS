from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_name', 'storage_used', 'is_staff', 'date_joined')
    list_filter  = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_name')
    ordering = ('-date_joined',)

    # Add the custom fields to the edit form
    fieldsets = UserAdmin.fieldsets + (
        ('NAS Info', {'fields': ('phone_name', 'storage_used')}),
    )
