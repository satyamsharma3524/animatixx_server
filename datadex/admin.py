from django.contrib import admin

from datadex.models import SiteAsset

# Register your models here.


class SiteAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image', 'created_at', 'updated_at')


admin.site.register(SiteAsset, SiteAssetAdmin)
