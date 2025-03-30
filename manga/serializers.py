from rest_framework import serializers
from manga.models import (
    Chapter, Comment, Manga, UserHistory)


class MangaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manga
        fields = '__all__'


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'replies']

    def get_replies(self, obj):
        return CommentSerializer(obj.replies.all(), many=True).data


class UserHistorySerializer(serializers.ModelSerializer):
    manga_title = serializers.ReadOnlyField(source="manga.title")
    manga_cover = serializers.ReadOnlyField(source="manga.cover_image")

    class Meta:
        model = UserHistory
        fields = [
            "id",
            "user",
            "manga",
            "manga_title",
            "manga_cover",
            "last_read_chapter",
            "progress_percentage",
            "is_completed",
            "last_interacted",
        ]
        read_only_fields = [
            "user", "last_interacted", "manga_title", "manga_cover"]
