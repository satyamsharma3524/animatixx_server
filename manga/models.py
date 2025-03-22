from django.db import models

# Create your models here.


class Tag(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Manga(models.Model):
    dex_id = models.CharField(max_length=255)
    anilist_id = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=500)
    alt_titles = models.JSONField(default=list, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    alt_description = models.JSONField(default=list, blank=True, null=True)
    original_language = models.CharField(max_length=255, null=True, blank=True)
    last_chapter = models.CharField(max_length=255, null=True, blank=True)
    completion_status = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="mangas")
    latest_chapter = models.CharField(max_length=255, null=True, blank=True)
    cover_image = models.CharField(max_length=500, null=True, blank=True)
    banner_image = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title[:50] + "..." if len(self.title) > 50 else self.title


class Chapter(models.Model):
    manga = models.ForeignKey(
        Manga, related_name="chapters", on_delete=models.CASCADE)
    chapter_number = models.CharField(max_length=255, null=True, blank=True)
    chapter_dex_id = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    release_date = models.DateTimeField(null=True, blank=True)
    images = models.JSONField(default=list, blank=True, null=True)
    datasaver_images = models.JSONField(default=list, blank=True, null=True)
    base_url = models.URLField(null=True, blank=True)
    hash_code = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["chapter_number"]

    def __str__(self):
        return self.manga.title[:50] + "..." if len(
            self.manga.title) > 50 else self.manga.title
