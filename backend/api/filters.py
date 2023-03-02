from django_filters import CharFilter, FilterSet, NumberFilter
from reviews.models import Title


class TitleFilter(FilterSet):
    """
    Title
    Поиск по полю slug жанра и категории.
    """

    genre = CharFilter(field_name='genre__slug', lookup_expr='icontains')
    category = CharFilter(field_name='category__slug', lookup_expr='icontains')
    name = CharFilter(field_name='name', lookup_expr='contains')
    year = NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('genre', 'category', 'name', 'year')
