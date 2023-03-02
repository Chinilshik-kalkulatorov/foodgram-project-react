from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title

REPEAT_REVIEW_ERROR = 'Нельзя добавить повторный отзыв!'
SCORE_ERROR = 'Оценка должна быть целым числом в пределах от 1 до 10!'
MAX_VALUE_SCORE_VALIDATOR = 10
MIN_VALUE_SCORE_VALIDATOR = 1


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Жанры."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer(many=False)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    def validate_score(self, score):
        if self.context.get('request').method == 'POST':
            if (
                type(score) != int
                or (score < MIN_VALUE_SCORE_VALIDATOR
                    or score > MAX_VALUE_SCORE_VALIDATOR)
            ):
                raise serializers.ValidationError(SCORE_ERROR)
        return score

    def validate(self, data):
        if self.context.get('request').method == 'POST':
            if Review.objects.filter(
                title=get_object_or_404(
                    Title,
                    id=self.context['view'].kwargs.get('title_id')
                ),
                author=self.context['request'].user
            ).exists():
                raise serializers.ValidationError(REPEAT_REVIEW_ERROR)
        return data

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
