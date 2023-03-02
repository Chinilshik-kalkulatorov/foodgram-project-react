from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets
from rest_framework.filters import SearchFilter
from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsAuthorAdminModeratorOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer)


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    filter_backends = DjangoFilterBackend
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorAdminModeratorOrReadOnly,
    )

    def get_title(self):
        return get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorAdminModeratorOrReadOnly,
    )

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )
