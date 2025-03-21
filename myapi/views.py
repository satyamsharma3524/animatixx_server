# from rest_framework.decorators import api_view
# from rest_framework.response import Response
from rest_framework import mixins, viewsets
# from rest_framework.pagination import PageNumberPagination
# from django.core.cache import cache

from manga.models import (
    Manga)
from manga.serializers import (
    MangaSerializer)


class MangaViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = MangaSerializer
    queryset = Manga.objects.all().order_by("-created_at")

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
