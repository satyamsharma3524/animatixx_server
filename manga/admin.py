from django.contrib import admin

from manga.models import Chapter, Manga, Tag

# Register your models here.


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'description', 'is_active', 'created_at',
        'updated_at'
    )


class MangaAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'dex_id', 'anilist_id', 'completion_status',
        'cover_image', 'banner_image', 'created_at', 'updated_at'
    )


class ChapterAdmin(admin.ModelAdmin):
    list_display = (
        'manga', 'chapter_number', 'title', 'release_date',
        'created_at', 'updated_at'
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Manga, MangaAdmin)
admin.site.register(Chapter, ChapterAdmin)
