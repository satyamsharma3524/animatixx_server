from django.db import models

# Create your models here.

class CarouselImage(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='static/carousel_images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MangaList(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='static/manga_images')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)