from django.urls import path
from . import views

urlpatterns = [
    path('manga/', views.MangaViewSet.as_view(
        {'get': 'list'}), name='mangalist'),
    path('manga/<int:manga_id>/chapters/', views.ChapterViewSet.as_view(
        {'get': 'list'}), name='chapterlist'),
]
