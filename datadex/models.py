from django.db import models

# Create your models here.


class SiteAsset(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='site_assets/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
