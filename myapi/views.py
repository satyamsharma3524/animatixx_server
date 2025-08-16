# from rest_framework.decorators import api_view
from manga.tasks import track_manga_view
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status
# from rest_framework.pagination import PageNumberPagination
# from django.core.cache import cache
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
    TagSerializer
)


class MangaViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = MangaSerializer
    queryset = Manga.objects.all().order_by("-created_at")
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

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
    serializer_class = MangaSerializer

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

        trending_ids = r.zrevrange("trending:manga:weekly", 0, 9)
        if trending_ids:
            trending = Manga.objects.filter(id__in=trending_ids)

        popular_ids = r.zrevrange("popular:manga", 0, 9)
        if popular_ids:
            popular = Manga.objects.filter(id__in=popular_ids)

        return Response({
            "recently_viewed": self.get_serializer(
                recently_viewed, many=True).data,
            "trending_now": self.get_serializer(
                trending, many=True).data,
            "popular": self.get_serializer(
                popular, many=True).data,
        })


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
    queryset = Tag.objects.filter(is_active=True)


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
