from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff",
                    "is_superuser", "is_premium", "data_saver")

    list_filter = ("is_premium", "data_saver", "is_staff",
                   "is_superuser", "is_active")

    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("is_premium", "data_saver")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("is_premium", "data_saver")}),
    )

    search_fields = ("username", "email")


admin.site.register(User, CustomUserAdmin)
