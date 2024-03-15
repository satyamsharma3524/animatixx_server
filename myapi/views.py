from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from myapi.models import CarouselImage
from myapi.serializers import CarouselImageSerializer

@api_view(['GET'])
def carousel(request):
    carousels = CarouselImage.objects.all()
    data = CarouselImageSerializer(carousels, many=True).data
    return Response({'images': data})