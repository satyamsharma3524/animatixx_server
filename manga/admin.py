from django.contrib import admin

from manga.models import Chapter, Comment, Manga, Tag

# Register your models here.


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'description', 'is_active', 'created_at',
        'updated_at'
    )


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1


class MangaAdmin(admin.ModelAdmin):
    inlines = [ChapterInline]
    list_display = (
        'title', 'dex_id', 'anilist_id', 'completion_status',
        'cover_image', 'banner_image', 'created_at', 'updated_at'
    )


class ChapterAdmin(admin.ModelAdmin):
    list_display = (
        'manga', 'chapter_number', 'chapter_dex_id', 'title', 'release_date',
        'created_at', 'updated_at'
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'content', 'created_at', 'updated_at'
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Manga, MangaAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Comment, CommentAdmin)
