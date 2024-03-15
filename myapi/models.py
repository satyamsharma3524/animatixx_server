from django.db import models

# Create your models here.

class CarouselImage(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='static/carousel_images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class MangaList(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='static/manga_images')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class MangaChapters(models.Model):
    manga = models.ForeignKey(MangaList, on_delete=models.CASCADE, related_name='manga_chapters')
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='static/manga_chapter_images')
    manga_file = models.FileField(upload_to='static/manga_chapter_files')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name