from django.contrib import admin

from myapi.models import CarouselImage, MangaList

# Register your models here.


class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'created_at', 'updated_at')

class MangaListAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description', 'created_at', 'updated_at')

admin.site.register(CarouselImage, CarouselImageAdmin)
admin.site.register(MangaList, MangaListAdmin)
