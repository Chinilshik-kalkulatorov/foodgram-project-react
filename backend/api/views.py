from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Subscription, User
from recipes.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from .filters import IngredientSearchFilter, RecipesFilter
from .pagination import LimitPagePagination
from .permissions import AdminOrAuthor, AdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeForSubscriptionersSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UsersSerializer)


class UsersViewSet(UserViewSet):
    """Вьюсет для модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny, )

    def subscribed(self, serializer, id=None):
        Subscriptioner = get_object_or_404(User, id=id)
        if self.request.user == Subscriptioner:
            return Response({'message': 'Нельзя подписаться на себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription = Subscription.objects.get_or_create(user=self.request.user,
                                              author=Subscriptioner)
        serializer = SubscriptionSerializer(Subscription[0])
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribed(self, serializer, id=None):
        Subscriptioner = get_object_or_404(User, id=id)
        Subscription.objects.filter(user=self.request.user,
                                    author=Subscriptioner).delete()
        return Response({'message': 'Вы успешно отписаны'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, serializer, id):
        if self.request.method == 'DELETE':
            return self.unsubscribed(serializer, id)
        return self.subscribed(serializer, id)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, serializer):
        Subscriptioning = Subscription.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(Subscriptioning)
        serializer = SubscriptionSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (AdminOrAuthor,)
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        if self.action == 'retrieve':
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_to_favorite_or_shopping_cart(self, request, pk, model_class, success_message):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            model_class.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeForSubscriptionersSerializer(recipe)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(model_class, user=request.user, recipe=recipe)
        deleted.delete()
        return Response({'message': success_message}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.add_to_favorite_or_shopping_cart(request, pk, Favorite, 'Рецепт успешно удален из избранного')

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.add_to_favorite_or_shopping_cart(request, pk, ShoppingCart, 'Рецепт успешно удален из списка покупок')

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = AmountIngredient.objects.filter(
            recipe__shopping_cart__user=user).values(
                'ingredients__name',
                'ingredients__measurement_unit').annotate(
                    total_amount=Sum('amount'))
        data = ingredients.values_list('ingredients__name',
                                       'ingredients__measurement_unit',
                                       'total_amount')
        shopping_cart = 'Список покупок:\n'
        for name, measure, amount in data:
            shopping_cart += (f'{name.capitalize()} {amount} {measure},\n')
        response = HttpResponse(shopping_cart, content_type='text/plain')
        return response
