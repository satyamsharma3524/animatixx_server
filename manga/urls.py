from django.urls import path
from manga.views import MangaSearchView

urlpatterns = [
    path('search/', MangaSearchView.as_view(), name='manga-search'),
]
