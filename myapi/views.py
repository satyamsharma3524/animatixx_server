from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
import multiprocessing
from functools import partial

from myapi.models import (
    CarouselImage, MangaChapters, MangaList)
from myapi.serializers import (
    CarouselImageSerializer,
    MangaChapterSerializer,
    MangaListSerializer)
from zipfile import ZipFile
from PIL import Image
import io
import base64


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
    cache_key = f'manga_chapters_{manga_pk}'
    data = cache.get(cache_key)

    if data is None:
        chapters = MangaChapters.objects.filter(manga__pk=manga_pk)
        data = MangaChapterSerializer(chapters, many=True).data
        cache.set(cache_key, data)
    return Response({'chapters': data})


class CustomPagination(PageNumberPagination):
    page_size = 5


def process_image(file_path, image_name):
    with ZipFile(file_path, 'r') as zip_ref:
        with zip_ref.open(image_name) as file:
            img = Image.open(file)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='WEBP', quality=10)
            img_byte_arr = img_byte_arr.getvalue()
            return base64.encodebytes(img_byte_arr).decode('ascii')


@api_view(['GET'])
def manga_chapters_images(request):
    chapter_pk = request.GET.get('pk')
    try:
        chapter = MangaChapters.objects.get(pk=chapter_pk)
    except MangaChapters.DoesNotExist:
        return Response(
            {"message": "Chapter not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    file_path = chapter.manga_file.path

    image_names = []
    with ZipFile(file_path, 'r') as zip_ref:
        image_names = zip_ref.namelist()

    with multiprocessing.Pool() as pool:
        func = partial(process_image, file_path)
        images = pool.map(func, image_names)

    paginator = CustomPagination()
    paginated_images = paginator.paginate_queryset(images, request)
    serialized_images = paginated_images

    # Check if the paginated response is already cached
    cache_key = f"manga_chapters_images_{chapter_pk}_{paginator.page.number}"
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        return paginator.get_paginated_response(cached_response)

    # Cache the paginated response
    cache.set(cache_key, serialized_images, timeout=None)
    return paginator.get_paginated_response(serialized_images)
