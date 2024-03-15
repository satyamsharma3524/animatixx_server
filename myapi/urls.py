from django.urls import path
from . import views

urlpatterns = [
    path('carousel/', views.carousel, name='carousel'),
    path('mangalist/', views.MangaViewSet.as_view({'get': 'list'}), name='mangalist'),
]