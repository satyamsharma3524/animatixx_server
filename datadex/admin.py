from django.contrib import admin

from datadex.models import WebsiteAsset

# Register your models here.


class WebsiteAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'uploaded_at')
    search_fields = ('name',)
    list_filter = ('asset_type',)
    ordering = ('-uploaded_at',)
    date_hierarchy = 'uploaded_at'


admin.site.register(WebsiteAsset, WebsiteAssetAdmin)
