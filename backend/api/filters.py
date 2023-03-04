from django_filters import FilterSet
from django_filters.filters import (CharFilter, AllValuesMultipleFilter, BooleanFilter)

from recipes.models import Ingredient, Recipe, Tag


class RecipesFilter(FilterSet):
    """"Фильтр для сортировки рецептов."""""
    tags = AllValuesMultipleFilter(field_name='tags__slug',
                                   label='tags',
                                   queryset=Tag.objects.all())
    favorite = BooleanFilter(method='get_favorite')
    shopping_cart = BooleanFilter(method='get_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'favorite', 'shopping_cart')

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if value == int(True) and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def get_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value == int(True) and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
