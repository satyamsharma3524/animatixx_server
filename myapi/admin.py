from django.contrib import admin

from myapi.models import CarouselImage

# Register your models here.


class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'created_at', 'updated_at')

admin.site.register(CarouselImage, CarouselImageAdmin)
