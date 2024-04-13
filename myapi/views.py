from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status

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
    chapters = MangaChapters.objects.filter(manga__pk=manga_pk)
    data = MangaChapterSerializer(chapters, many=True).data
    return Response({'chapters': data})


@api_view(['GET'])
def manga_chapters_images(request):
    chapter_pk = request.GET.get('pk')
    try:
        chapter = MangaChapters.objects.get(pk=chapter_pk)
    except MangaChapters.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    file_path = chapter.manga_file.path

    with ZipFile(file_path, 'r') as zip_ref:
        image_names = zip_ref.namelist()
        images = []
        for image_name in image_names:
            with zip_ref.open(image_name) as file:
                img = Image.open(file)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                images.append(
                    base64.encodebytes(img_byte_arr).decode('ascii'))

    return Response({'images': images})
