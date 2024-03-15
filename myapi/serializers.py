from rest_framework import serializers
from myapi.models import CarouselImage, MangaList


class CarouselImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselImage
        fields = '__all__'

class MangaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MangaList
        fields = '__all__'