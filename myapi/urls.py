from django.urls import path
from . import views

urlpatterns = [
    path('carousel/', views.carousel, name='carousel'),
]