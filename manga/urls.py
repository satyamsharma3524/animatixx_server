from django.urls import path
from manga.views import MangaSearchView, image_proxy

urlpatterns = [
    path('search/', MangaSearchView.as_view(), name='manga-search'),
    path('image-proxy/', image_proxy, name='image-proxy'),
]
