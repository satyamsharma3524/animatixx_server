# from rest_framework.decorators import api_view
import random
from manga.tasks import track_manga_view
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status
# from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from utils.redis_client import r
from django.db.models import Case, When

from manga.models import (
    Chapter,
    Comment,
    Manga,
    Tag
)
from manga.serializers import (
    ChapterSerializer,
    CommentSerializer,
    MangaSerializer,
    MangaListSerializer,
    MangaCarouselSerializer,
    TagSerializer
)


class MangaViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = MangaSerializer
    queryset = Manga.objects.all().order_by("-created_at")
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        if self.action == "list":
            return MangaListSerializer
        return MangaSerializer

    def list(self, request, *args, **kwargs):
        queryset = Manga.objects.filter(
            cover_image__isnull=False
        ).exclude(
            cover_image=''
        ).order_by("-created_at")

        # 🔹 filter by tags (case-insensitive match)
        tag_param = request.query_params.get("tags")
        if tag_param:
            queryset = queryset.filter(tags__title__iexact=tag_param)

        self.queryset = queryset
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        manga_id = kwargs.get("pk")
        user_id = request.user.id if request.user.is_authenticated else None
        track_manga_view.delay(user_id, manga_id)
        return response


class HomeMangaViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Manga.objects.none()
    serializer_class = MangaListSerializer

    def list(self, request):
        user_id = request.user.id if request.user.is_authenticated else None
        recently_viewed = []
        trending = []
        popular = []

        if user_id:
            recent_ids = r.lrange(f"user:{user_id}:recent_manga", 0, 9)
            if recent_ids:
                preserved = Case(*[When(id=pk, then=pos)
                                   for pos, pk in enumerate(recent_ids)])
                recently_viewed = Manga.objects.filter(
                    id__in=recent_ids).order_by(preserved)

        # ✅ cache trending for 1 hour
        trending = cache.get("home:trending")
        if trending is None:
            trending_ids = r.zrevrange("trending:manga:weekly", 0, 9)
            if trending_ids:
                trending = list(Manga.objects.filter(id__in=trending_ids))
                cache.set("home:trending", trending, timeout=3600)
            else:
                trending = []

        # ✅ cache popular for 1 hour
        popular = cache.get("home:popular")
        if popular is None:
            popular_ids = r.zrevrange("popular:manga", 0, 9)
            if popular_ids:
                popular = list(Manga.objects.filter(id__in=popular_ids))
                cache.set("home:popular", popular, timeout=3600)
            else:
                popular = []

        return Response({
            "recently_viewed": self.get_serializer(
                recently_viewed, many=True).data,
            "trending_now": self.get_serializer(trending, many=True).data,
            "popular": self.get_serializer(popular, many=True).data,
        })


class CarouselViewSet(viewsets.ViewSet):
    """
    Homepage Carousel API
    Returns 3–5 mangas that are both in trending and popular,
    and have a banner_image.
    """
    serializer_class = MangaCarouselSerializer

    def list(self, request):
        cache_key = "homepage:carousel"
        data = cache.get(cache_key)
        if data:
            return Response(data)

        # Get IDs from Redis
        # trending_ids = set(r.zrevrange("trending:manga:weekly", 0, 49))
        # popular_ids = set(r.zrevrange("popular:manga", 0, 49))
        # common_ids = list(trending_ids & popular_ids)

        # queryset = Manga.objects.filter(
        #     id__in=common_ids,
        #     banner_image__isnull=False
        # )[:5]

        # ✅ Get all mangas that have a banner
        banner_mangas = Manga.objects.filter(banner_image__isnull=False)

        # ✅ Randomly pick 5
        manga_ids = list(banner_mangas.values_list("id", flat=True))
        selected_ids = random.sample(manga_ids, min(5, len(manga_ids)))

        queryset = banner_mangas.filter(id__in=selected_ids)

        serialized = self.serializer_class(queryset, many=True).data
        # ✅ Cache for 6 hours
        cache.set(cache_key, serialized, timeout=6 * 60 * 60)

        return Response(serialized)


class ChapterViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = ChapterSerializer
    queryset = Chapter.objects.all().order_by("-chapter_number")

    def list(self, request, *args, **kwargs):
        manga_pk = kwargs.get("manga_pk")
        print(f"manga_pk: {manga_pk}")
        self.queryset = self.queryset.annotate(
            chapter_number_int=Cast("chapter_number", IntegerField())
        ).filter(manga__pk=manga_pk).order_by("chapter_number_int")
        return super().list(request, *args, **kwargs)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer

    def get_queryset(self):
        tags = cache.get("tags:active")
        if tags is None:
            tags = list(Tag.objects.filter(is_active=True))
            cache.set("tags:active", tags, timeout=3600)  # 1 hour
        return tags


class CommentViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for manga comments."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Filter comments for a specific manga."""
        manga_pk = self.kwargs.get("manga_pk")
        if manga_pk:
            return Comment.objects.filter(
                manga_id=manga_pk).select_related(
                    'user', 'manga').prefetch_related('replies')
        return Comment.objects.all().select_related(
            'user', 'manga').prefetch_related('replies')

    def perform_create(self, serializer):
        """Ensure comments are associated with the correct manga."""
        manga_pk = self.kwargs.get("manga_pk")
        if not manga_pk:
            raise ValidationError(
                {"error": "Manga ID is required."})
        try:
            manga = Manga.objects.get(pk=manga_pk)
        except Manga.DoesNotExist:
            raise ValidationError({"error": "Manga not found."})

        parent_id = self.request.data.get("parent")
        parent_comment = Comment.objects.filter(
            id=parent_id).first() if parent_id else None

        serializer.save(
            user=self.request.user,
            manga=manga, parent=parent_comment)

    def update(self, request, *args, **kwargs):
        """Ensure users can only edit their own comments."""
        comment = self.get_object()
        if request.user != comment.user:
            return Response(
                {"error": "You can only edit your own comments."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Ensure users can only delete their own comments."""
        comment = self.get_object()
        if request.user != comment.user:
            return Response(
                {"error": "You can only delete your own comments."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
