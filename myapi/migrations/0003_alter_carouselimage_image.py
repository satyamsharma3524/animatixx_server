# Generated by Django 5.0.3 on 2024-03-15 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapi', '0002_alter_carouselimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carouselimage',
            name='image',
            field=models.ImageField(upload_to='static/carousel_images'),
        ),
    ]
