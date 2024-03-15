from rest_framework import serializers
from myapi.models import CarouselImage


class CarouselImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselImage
        fields = '__all__'