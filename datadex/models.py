from django.db import models

# Create your models here.


class WebsiteAsset(models.Model):
    ASSET_TYPES = [
        ('banner', 'Banner'),
        ('icon', 'Icon'),
        ('logo', 'Logo'),
        ('background', 'Background'),
        ('thumbnail', 'Thumbnail'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    image = models.ImageField(upload_to='assets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset_type.capitalize()} - {self.name}"
