from django.urls import path
from . import views

urlpatterns = [
    path('carousel/', views.carousel, name='carousel'),
    path('mangalist/', views.MangaViewSet.as_view(
        {'get': 'list'}), name='mangalist'),
    path('mangachapter/',
         views.manga_chapter_list, name='mangachapter'),
    path('chapter_images/',
         views.manga_chapters_images, name='mangachapters_images'),
]
