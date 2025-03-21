from django.urls import path
from . import views

urlpatterns = [
    path('manga/', views.MangaViewSet.as_view(
        {'get': 'list'}), name='mangalist'),
]
