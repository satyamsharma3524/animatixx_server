from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import mixins, viewsets

from myapi.models import CarouselImage, MangaChapters, MangaList
from myapi.serializers import CarouselImageSerializer, MangaChapterSerializer, MangaListSerializer


@api_view(['GET'])
def carousel(request):
    carousels = CarouselImage.objects.all()
    data = CarouselImageSerializer(carousels, many=True).data
    return Response({'images': data})


class MangaViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = MangaListSerializer
    queryset = MangaList.objects.all().order_by("-created_at")

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@api_view(['GET'])
def manga_chapter_list(request):
    manga_pk = request.GET.get('pk')
    chapters = MangaChapters.objects.filter(manga__pk=manga_pk)
    data = MangaChapterSerializer(chapters, many=True).data
    return Response({'chapters': data})
