from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from .views import (
    HomeMangaViewSet, MangaViewSet, ChapterViewSet, CommentViewSet)

# Main router
router = DefaultRouter()
router.register(r'manga', MangaViewSet, basename='manga')
router.register(r'home', HomeMangaViewSet, basename='home')

# Nested router for chapters
manga_router = NestedDefaultRouter(router, r'manga', lookup='manga')
manga_router.register(r'chapters', ChapterViewSet, basename='manga-chapters')
manga_router.register(r'comments', CommentViewSet, basename='manga-comments')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(manga_router.urls)),
]
