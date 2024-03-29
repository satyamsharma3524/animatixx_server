# Generated by Django 5.0.3 on 2024-03-15 08:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapi', '0004_mangalist'),
    ]

    operations = [
        migrations.CreateModel(
            name='MangaChapters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='static/manga_chapter_images')),
                ('manga_file', models.FileField(upload_to='static/manga_chapter_files')),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('manga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manga_chapters', to='myapi.mangalist')),
            ],
        ),
    ]
