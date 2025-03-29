# from rest_framework.decorators import api_view
# from rest_framework.response import Response
from rest_framework import mixins, viewsets
# from rest_framework.pagination import PageNumberPagination
# from django.core.cache import cache
from django.db.models import IntegerField
from django.db.models.functions import Cast

from manga.models import (
    Chapter,
    Manga
)
from manga.serializers import (
    ChapterSerializer,
    MangaSerializer
)


class MangaViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = MangaSerializer
    queryset = Manga.objects.all().order_by("-created_at")

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ChapterViewSet(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = ChapterSerializer
    queryset = Chapter.objects.all().order_by("-chapter_number")

    def list(self, request, *args, **kwargs):
        manga_id = kwargs.get("manga_id")
        print(f"manga_id: {manga_id}")
        self.queryset = self.queryset.annotate(
            chapter_number_int=Cast("chapter_number", IntegerField())
        ).filter(manga__pk=manga_id).order_by("chapter_number_int")
        return super().list(request, *args, **kwargs)
